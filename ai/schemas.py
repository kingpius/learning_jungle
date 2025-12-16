from dataclasses import dataclass
from typing import List, Sequence

from .exceptions import AIValidationError


@dataclass
class MultipleChoiceQuestion:
    question_text: str
    options: Sequence[str]
    correct_option: str  # Literal "A"-"D"
    difficulty: str

    def as_ordered_dict(self) -> dict:
        return {
            "question_text": self.question_text,
            "options": list(self.options),
            "correct_option": self.correct_option,
            "difficulty": self.difficulty,
        }


def _validate_option_label(index: int) -> str:
    mapping = {0: "A", 1: "B", 2: "C", 3: "D"}
    try:
        return mapping[index]
    except KeyError as exc:
        raise AIValidationError(f"Invalid correct option index: {index}") from exc


def parse_questions(payload: dict) -> List[MultipleChoiceQuestion]:
    if "questions" not in payload or not isinstance(payload["questions"], list):
        raise AIValidationError("Payload missing 'questions' list.")

    parsed: List[MultipleChoiceQuestion] = []
    for idx, row in enumerate(payload["questions"], start=1):
        if not isinstance(row, dict):
            raise AIValidationError(f"Question #{idx} is not an object.")

        question_text = row.get("question_text")
        options = row.get("options")
        correct_index = row.get("correct_answer_index")
        difficulty = row.get("difficulty")

        if not question_text or not isinstance(question_text, str):
            raise AIValidationError(f"Question #{idx} missing text.")
        if not isinstance(options, list) or len(options) != 4:
            raise AIValidationError(f"Question #{idx} must include 4 options.")
        if not isinstance(correct_index, int):
            raise AIValidationError(f"Question #{idx} missing correct index.")
        if not difficulty or not isinstance(difficulty, str):
            raise AIValidationError(f"Question #{idx} missing difficulty.")

        option_label = _validate_option_label(correct_index)
        parsed.append(
            MultipleChoiceQuestion(
                question_text=question_text.strip(),
                options=[opt.strip() for opt in options],
                correct_option=option_label,
                difficulty=difficulty.strip().lower(),
            )
        )

    if not parsed:
        raise AIValidationError("No questions returned by provider.")

    return parsed
