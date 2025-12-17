## Diagnostics UI & API (LJ-008)

Server-rendered child flow:
- `GET/POST /assessments/start/<child_id>/` (`diagnostic_start`) — create or resume Maths diagnostic for a parent-owned child; generates questions via AI if needed.
- `GET/POST /assessments/questions/<test_id>/` (`diagnostic_questions`) — render questions, save answers, submit to score and complete; completed tests redirect to results.
- `GET /assessments/results/<test_id>/` (`diagnostic_results`) — read-only summary with score, rank, treasure status, and answer review.

API endpoints (for QA/integration; require login + parent ownership):
- `POST /assessments/api/tests/<child_id>/` (`create_diagnostic_test`) — create a Maths diagnostic (AI question generation). Returns 200 with the existing pending test, 409 if already completed for that child.
- `POST /assessments/api/tests/<test_id>/complete/` (`complete_diagnostic_test`) — scores from stored responses, requires all questions answered, then marks complete (fires rank + treasure unlock signals).

Notes:
- Single attempt per child for Maths diagnostics; completed children are redirected to results and cannot restart.

Templates: diagnostics screens use the design system in `assessments/templates/assessments/diagnostics/` with shared styles from `core/design-system.css`.
