from textwrap import dedent

PROMPT_VERSION = "lj-ai-maths-v1"


def build_maths_prompt(*, age: int, year_group: int, n_questions: int) -> str:
    """
    Builds the deterministic prompt for generating maths MCQs.
    Child-identifying data is excluded; only age/year context is provided.
    """
    base = f"""
    You are an educational content engine for UK National Curriculum maths.
    Generate {n_questions} multiple-choice diagnostic questions for a child
    aged {age} in Year {year_group}. Each question must include:
    - question_text
    - four answer options labelled A-D
    - correct_answer_index (0-3)
    - difficulty tag (easy, medium, hard)

    Guardrails:
    - Stay strictly within Year {year_group} expectations.
    - Prioritize number sense, arithmetic, and problem-solving aligned to UK curriculum.
    - Avoid trick questions, cultural references, or adult themes.
    - Keep wording concise and age-appropriate.
    - Responses must be valid JSON with a top-level "questions" list.
    """
    return dedent(base).strip()
