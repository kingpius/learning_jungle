import hashlib
import json
import os
from dataclasses import dataclass
from typing import Sequence

from .exceptions import AIProviderError, AIServiceError, AIValidationError
from .prompts import PROMPT_VERSION, build_maths_prompt
from .providers import call_llm
from .schemas import MultipleChoiceQuestion, parse_questions


@dataclass(frozen=True)
class GenerationResult:
    prompt_version: str
    prompt_text: str
    response_text: str
    seed: str
    questions: Sequence[MultipleChoiceQuestion]


def compute_seed(*, age: int, year_group: int, n_questions: int) -> str:
    fingerprint = f"{PROMPT_VERSION}:{age}:{year_group}:{n_questions}"
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return digest[:16]


def generate_maths_mcqs(
    *, age: int, year_group: int, n_questions: int
) -> GenerationResult:
    prompt = build_maths_prompt(age=age, year_group=year_group, n_questions=n_questions)
    seed = compute_seed(age=age, year_group=year_group, n_questions=n_questions)

    timeout = int(os.environ.get("AI_TIMEOUT_SECONDS", "30"))
    response_text = call_llm(prompt, seed=seed, timeout=timeout)

    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise AIValidationError("AI response must be valid JSON.") from exc

    questions = parse_questions(payload)
    return GenerationResult(
        prompt_version=PROMPT_VERSION,
        prompt_text=prompt,
        response_text=response_text,
        seed=seed,
        questions=questions,
    )
