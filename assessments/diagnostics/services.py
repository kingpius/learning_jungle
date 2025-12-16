import json
import time
from typing import Optional, Sequence

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from assessments.models import AIRequestLog, DiagnosticQuestion, DiagnosticTest
from ai.exceptions import AIProviderError, AIValidationError
from ai.maths_diagnostic import GenerationResult, compute_seed, generate_maths_mcqs
from ai.prompts import PROMPT_VERSION, build_maths_prompt


class DiagnosticGenerationError(Exception):
    """Raised when the diagnostic question generation fails for user-visible reasons."""


def _get_question_target() -> int:
    default = 10
    return getattr(settings, "MATHS_DIAGNOSTIC_QUESTION_COUNT", default)


def ensure_maths_questions_for_test(
    test: DiagnosticTest, *, n_questions: Optional[int] = None
) -> Sequence[DiagnosticQuestion]:
    if test.subject != DiagnosticTest.Subject.MATHS:
        raise ValidationError("AI generation currently supports Maths only.")

    if test.is_completed:
        raise ValidationError("Cannot generate questions for a completed test.")

    existing = test.questions.order_by("order")
    if existing.exists():
        return list(existing)

    question_total = n_questions or _get_question_target()
    start = time.monotonic()
    prompt_text = build_maths_prompt(
        age=test.child.age, year_group=test.child.year_group, n_questions=question_total
    )
    seed = compute_seed(age=test.child.age, year_group=test.child.year_group, n_questions=question_total)
    log_kwargs = {
        "test": test,
        "prompt_version": PROMPT_VERSION,
        "seed": seed,
        "prompt_excerpt": prompt_text[:500],
        "response_excerpt": "",
    }

    provider_name = getattr(settings, "AI_PROVIDER", "default")
    try:
        generation = generate_maths_mcqs(
            age=test.child.age, year_group=test.child.year_group, n_questions=question_total
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        log_kwargs.update(
            {
                "prompt_version": generation.prompt_version,
                "seed": generation.seed,
                "prompt_excerpt": generation.prompt_text[:500],
                "response_excerpt": generation.response_text[:500],
                "latency_ms": duration_ms,
            }
        )
        saved_questions = _persist_questions(test, generation)
        AIRequestLog.objects.create(
            provider=provider_name,
            status=AIRequestLog.Status.SUCCESS,
            **log_kwargs,
        )
        return saved_questions
    except (AIProviderError, AIValidationError) as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        log_kwargs.update(
            {
                "latency_ms": duration_ms,
            }
        )
        AIRequestLog.objects.create(
            provider=provider_name,
            status=AIRequestLog.Status.FAILURE,
            error_message=str(exc),
            **log_kwargs,
        )
        raise DiagnosticGenerationError(str(exc)) from exc


def _persist_questions(
    test: DiagnosticTest, generation: GenerationResult
) -> Sequence[DiagnosticQuestion]:
    with transaction.atomic():
        payload = []
        for index, question in enumerate(generation.questions, start=1):
            payload.append(
                DiagnosticQuestion(
                    test=test,
                    prompt_version=generation.prompt_version,
                    seed=generation.seed,
                    order=index,
                    question_text=question.question_text,
                    option_a=question.options[0],
                    option_b=question.options[1],
                    option_c=question.options[2],
                    option_d=question.options[3],
                    correct_option=question.correct_option,
                    difficulty=question.difficulty,
                )
            )

        created = DiagnosticQuestion.objects.bulk_create(payload)
        return created
