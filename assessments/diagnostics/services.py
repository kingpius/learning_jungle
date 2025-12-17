import json
import time
from typing import Optional, Sequence

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from assessments.models import (
    AIRequestLog,
    DiagnosticQuestion,
    DiagnosticTest,
    DiagnosticResponse,
)
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
        if getattr(settings, "AI_FALLBACK_MODE", "error") == "stub":
            return _persist_stub_questions(test, question_total)
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


def _persist_stub_questions(test: DiagnosticTest, total: int) -> Sequence[DiagnosticQuestion]:
    """
    Safe fallback for production environments without AI credentials.
    Generates deterministic, simple Maths MCQs so the diagnostic flow does not crash.
    """
    stubs = [
        ("2 + 3 = ?", ["4", "5", "6", "7"], "B"),
        ("10 - 4 = ?", ["4", "5", "6", "7"], "C"),
        ("6 + 7 = ?", ["11", "12", "13", "14"], "C"),
        ("9 - 3 = ?", ["5", "6", "7", "8"], "B"),
        ("3 + 8 = ?", ["10", "11", "12", "13"], "B"),
        ("12 - 5 = ?", ["6", "7", "8", "9"], "B"),
        ("4 + 4 = ?", ["6", "7", "8", "9"], "C"),
        ("15 - 9 = ?", ["5", "6", "7", "8"], "B"),
        ("7 + 5 = ?", ["11", "12", "13", "14"], "B"),
        ("8 - 2 = ?", ["5", "6", "7", "8"], "B"),
    ]
    payload = []
    for index in range(1, total + 1):
        question_text, options, correct = stubs[(index - 1) % len(stubs)]
        payload.append(
            DiagnosticQuestion(
                test=test,
                prompt_version="stub",
                seed="stub",
                order=index,
                question_text=question_text,
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                correct_option=correct,
                difficulty="easy",
            )
        )
    with transaction.atomic():
        return DiagnosticQuestion.objects.bulk_create(payload)


def create_or_resume_maths_test(child) -> DiagnosticTest:
    """
    Return an existing incomplete Maths diagnostic or create a new one
    with generated questions for the child.
    """
    if child.diagnostic_tests.filter(
        subject=DiagnosticTest.Subject.MATHS, is_completed=True
    ).exists():
        raise ValidationError("Maths diagnostic already completed for this child.")

    existing = (
        child.diagnostic_tests.filter(
            subject=DiagnosticTest.Subject.MATHS, is_completed=False
        )
        .order_by("-created_at")
        .first()
    )
    if existing:
        return existing

    total = _get_question_target()
    test = DiagnosticTest.objects.create(
        child=child,
        subject=DiagnosticTest.Subject.MATHS,
        total_questions=total,
    )
    ensure_maths_questions_for_test(test, n_questions=total)
    return test


def record_responses(test: DiagnosticTest, answers: dict[int, str]) -> None:
    """
    Persist child selections per question.
    """
    valid_ids = set(test.questions.values_list("id", flat=True))
    for question_id, option in answers.items():
        if question_id not in valid_ids:
            continue

        DiagnosticResponse.objects.update_or_create(
            test=test,
            question_id=question_id,
            defaults={"selected_option": option},
        )


def score_test_from_responses(test: DiagnosticTest) -> int:
    """
    Calculates correct answers from stored responses and completes the test.
    Raises ValidationError if not all questions are answered.
    """
    if test.is_completed:
        return test.correct_answers

    questions = list(test.questions.all())
    responses = {
        response.question_id: response
        for response in DiagnosticResponse.objects.filter(test=test)
    }
    missing = [q.id for q in questions if q.id not in responses]
    if missing:
        raise ValidationError("All questions must be answered before submission.")

    correct = sum(
        1
        for question in questions
        if responses[question.id].selected_option == question.correct_option
    )
    test.correct_answers = correct
    test.save(update_fields=["correct_answers"])
    test.complete()
    return correct
