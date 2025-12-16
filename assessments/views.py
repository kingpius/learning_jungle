import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from children.models import Child

from .models import DiagnosticTest
from .diagnostics.services import (
    DiagnosticGenerationError,
    ensure_maths_questions_for_test,
)


def _payload_from_request(request):
    if request.headers.get("Content-Type", "").startswith("application/json"):
        try:
            body = request.body.decode() if request.body else "{}"
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    return request.POST


def _parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer.")


@login_required
@require_http_methods(["POST"])
def create_diagnostic_test(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    payload = _payload_from_request(request)

    subject = payload.get("subject")
    if not subject:
        return JsonResponse({"error": "Subject is required."}, status=400)

    try:
        total_questions = _parse_int(payload.get("total_questions"), "total_questions")
        correct_answers = _parse_int(payload.get("correct_answers", 0), "correct_answers")
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    diagnostic_test = DiagnosticTest(
        child=child,
        subject=subject,
        total_questions=total_questions,
        correct_answers=correct_answers,
    )
    try:
        diagnostic_test.full_clean()
    except ValidationError as exc:
        message = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
        return JsonResponse({"error": message}, status=400)

    diagnostic_test.save()
    if diagnostic_test.subject == DiagnosticTest.Subject.MATHS:
        try:
            ensure_maths_questions_for_test(diagnostic_test)
        except ValidationError as exc:
            diagnostic_test.delete()
            message = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            return JsonResponse({"error": message}, status=400)
        except DiagnosticGenerationError as exc:
            diagnostic_test.delete()
            return JsonResponse({"error": str(exc)}, status=503)
    response = {
        "id": str(diagnostic_test.id),
        "child_id": str(child.id),
        "subject": diagnostic_test.subject,
        "score_percentage": str(diagnostic_test.score_percentage),
        "is_completed": diagnostic_test.is_completed,
    }
    return JsonResponse(response, status=201)


@login_required
@require_http_methods(["POST"])
def complete_diagnostic_test(request, test_id):
    diagnostic_test = get_object_or_404(
        DiagnosticTest, id=test_id, child__parent=request.user
    )
    completed_now = diagnostic_test.complete()

    response = {
        "id": str(diagnostic_test.id),
        "status": "completed" if completed_now else "already_completed",
        "completed_at": diagnostic_test.completed_at.isoformat()
        if diagnostic_test.completed_at
        else None,
        "score_percentage": str(diagnostic_test.score_percentage),
    }
    return JsonResponse(response, status=200)
