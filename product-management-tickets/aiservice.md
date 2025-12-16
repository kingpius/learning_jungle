## 🤖 AI Service Reference — Diagnostics Maths Generator (LJ-006 Companion)

This document governs every AI touchpoint for LJ-006. The team must treat it as the single source of truth for **policy, architecture, and testing**. Deviations require PM approval.

---

### 1. Mission & Guardrails
- **Curriculum-aligned**: Maths only, UK National Curriculum, aligned to the child’s age & year group.
- **Safe & Age-appropriate**: No sensitive topics, adult themes, or off-curriculum trivia.
- **Deterministic by design**: Same inputs → same outputs (via deterministic prompt, low temperature, caching).
- **Explainable**: Log every prompt + response (with child PII removed) for audit.
- **No AI in views**: All AI calls live in `ai/` service modules; views/controllers call deterministic services only.
- **Fail-safe**: On provider failure, service surfaces controlled errors and never stores partial data.

---

### 2. Service Architecture
```
assessments (DiagnosticTest)
    └── diagnostics/services.py::ensure_maths_questions_for_test()
            └── ai/maths_diagnostic.py::generate_maths_mcqs()
                    ├── ai/prompts.py (prompt builder v1)
                    ├── ai/providers.py::call_llm()
                    └── ai/schemas.py (MCQ dataclass)
```
- **Caching Layer**: Persist generated MCQs in `DiagnosticQuestion` table keyed by `DiagnosticTest`. Reuse if present.
- **Configuration**: Environment-driven (`AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT_SECONDS`).
- **Logging**: `AI_REQUEST_LOG` table (or structured log) capturing `test_id`, `prompt_version`, seed, truncated response, latency, success/failure.
- **Prompt Versioning**: `PROMPT_VERSION = "lj-ai-maths-v1"` stored in `ai/prompts.py`; bump version when changing instructions.

---

### 3. Implementation Checklist (Full Stack Engineer)
1. Create `ai/` module with `prompts.py`, `schemas.py`, `providers.py`, `maths_diagnostic.py`.
2. Implement deterministic seed via `(prompt_version, subject, age, year, n_questions)`.
3. Add database model(s):
   - `DiagnosticQuestion` (belongs to `DiagnosticTest`, stores four options + correct answer + difficulty).
   - `AIRequestLog` (optional but recommended for audit).
4. Add service `ensure_maths_questions_for_test(test, n_questions=10)`:
   - Abort if test not Maths or already completed.
   - Skip generation if questions already exist.
   - Generate + persist MCQs within a transaction.
5. Wire service into DiagnosticTest creation flow (not completion). Never invoked from templates or asynchronous tasks without PM approval.
6. Update settings to load provider configuration from environment; no secrets in code.

---

### 4. Testing Expectations (Test Engineer)
| Scenario | Expected Behaviour |
| --- | --- |
| AI returns valid payload | MCQs persisted, deterministic repeat. |
| AI returns invalid schema | Service raises `AIValidationError`; no questions saved. |
| Provider times out | Controlled exception bubbled up; logs entry with failure. |
| Duplicate call for same test | Service detects existing questions and no-ops. |
| Cross-subject call | Service rejects with clear error message. |

Guidance:
- Use deterministic fixtures/mocks for AI responses; never hit live provider during automated tests.
- Validate logging by asserting `AI_REQUEST_LOG` (or log handler) receives expected metadata.
- Include integration test covering DiagnosticTest creation → question generation → question retrieval.

---

### 5. Operational Runbook
1. **Before deploy**: `python manage.py migrate` (new question/log models) and configure AI env vars.
2. **Monitoring**: Track AI latency, failure rate, prompt version adoption.
3. **Rollback**: If AI service misbehaves, disable generation via feature flag (`AI_GENERATION_ENABLED=false`) and rely on existing static questions (if available).
4. **Security**: Rotate API keys quarterly; ensure prompts never include child names (use year/age only).

---

### 6. Approvals
- PM owns scope + prompt changes.
- Full Stack Engineer owns implementation + deployment.
- Test Engineer signs off only when deterministic tests pass and logging is verifiable.
