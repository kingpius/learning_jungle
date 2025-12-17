from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from children.models import Child
from rewards.models import TreasureChest

from .diagnostics import services
from .models import DiagnosticResponse, DiagnosticTest


@login_required
def diagnostic_start(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    pending_test = (
        DiagnosticTest.objects.filter(
            child=child, subject=DiagnosticTest.Subject.MATHS, is_completed=False
        )
        .order_by("-created_at")
        .first()
    )
    last_completed = (
        DiagnosticTest.objects.filter(
            child=child, subject=DiagnosticTest.Subject.MATHS, is_completed=True
        )
        .order_by("-completed_at")
        .first()
    )

    if request.method == "POST":
        if last_completed and not pending_test:
            return redirect("assessments:diagnostic_results", test_id=last_completed.id)

        test = services.create_or_resume_maths_test(child)
        return redirect("assessments:diagnostic_questions", test_id=test.id)

    context = {
        "child": child,
        "pending_test": pending_test,
        "last_completed": last_completed,
        "locked": bool(last_completed and not pending_test),
    }
    return render(request, "assessments/diagnostics/start.html", context)


@login_required
def diagnostic_questions(request, test_id):
    test = get_object_or_404(
        DiagnosticTest.objects.select_related("child"),
        id=test_id,
        child__parent=request.user,
    )
    questions = list(test.questions.all())
    responses_map = {
        resp.question_id: resp.selected_option for resp in test.responses.all()
    }
    for question in questions:
        question.option_pairs = [
            ("A", question.option_a),
            ("B", question.option_b),
            ("C", question.option_c),
            ("D", question.option_d),
        ]
        question.selected_choice = responses_map.get(question.id)

    if request.method == "POST":
        if test.is_completed:
            return redirect("assessments:diagnostic_results", test_id=test.id)

        action = request.POST.get("action")
        answers = {}
        for question in questions:
            answer = request.POST.get(f"answer_{question.id}")
            if answer:
                answers[question.id] = answer

        saved = False
        errors = []
        with transaction.atomic():
            services.record_responses(test, answers)
            saved = action == "save"

            if action == "submit":
                try:
                    services.score_test_from_responses(test)
                    return redirect("assessments:diagnostic_results", test_id=test.id)
                except ValidationError:
                    errors.append("Please answer all questions before submitting.")
                    transaction.set_rollback(True)

        responses_map = {
            resp.question_id: resp.selected_option for resp in test.responses.all()
        }
        for question in questions:
            question.selected_choice = responses_map.get(question.id)

        context = {
            "test": test,
            "child": test.child,
            "questions": questions,
            "read_only": False,
            "saved": saved,
            "errors": errors,
        }
        return render(request, "assessments/diagnostics/questions.html", context)

    if test.is_completed:
        return redirect("assessments:diagnostic_results", test_id=test.id)

    context = {
        "test": test,
        "child": test.child,
        "questions": questions,
        "read_only": False,
        "saved": False,
        "errors": [],
    }
    return render(request, "assessments/diagnostics/questions.html", context)


@login_required
def diagnostic_results(request, test_id):
    test = get_object_or_404(
        DiagnosticTest.objects.select_related("child"),
        id=test_id,
        child__parent=request.user,
    )
    if not test.is_completed:
        raise Http404("Test has not been completed yet.")

    treasure_chest = TreasureChest.objects.filter(child=test.child).first()

    responses = (
        DiagnosticResponse.objects.filter(test=test)
        .select_related("question")
        .order_by("question__order")
    )
    enhanced_responses = []
    for response in responses:
        q = response.question
        enhanced_responses.append(
            {
                "question": q,
                "selected_option": response.selected_option,
                "selected_text": getattr(q, f"option_{response.selected_option.lower()}"),
                "correct_text": getattr(q, f"option_{q.correct_option.lower()}"),
            }
        )

    context = {
        "test": test,
        "child": test.child,
        "treasure_chest": treasure_chest,
        "responses": enhanced_responses,
    }
    return render(request, "assessments/diagnostics/results.html", context)


@login_required
def create_diagnostic_test(request, child_id):
    if request.method != "POST":
        raise Http404()

    child = get_object_or_404(Child, id=child_id, parent=request.user)
    subject = request.POST.get("subject")
    total_questions = int(request.POST.get("total_questions", 10))

    if subject != DiagnosticTest.Subject.MATHS:
        return JsonResponse({"error": "Only Maths diagnostics are supported."}, status=400)

    if DiagnosticTest.objects.filter(
        child=child, subject=subject, is_completed=True
    ).exists():
        return JsonResponse(
            {"error": "Maths diagnostic already completed for this child."}, status=409
        )

    existing = DiagnosticTest.objects.filter(
        child=child, subject=subject, is_completed=False
    ).first()
    if existing:
        return JsonResponse(
            {"id": str(existing.id), "subject": existing.subject, "rank": existing.rank},
            status=200,
        )

    test = DiagnosticTest(
        child=child,
        subject=subject,
        total_questions=total_questions,
        correct_answers=0,
    )
    try:
        test.full_clean()
    except Exception:
        return JsonResponse({"error": "Invalid payload"}, status=400)

    test.save()
    try:
        services.ensure_maths_questions_for_test(test, n_questions=total_questions)
    except services.DiagnosticGenerationError as exc:
        test.delete()
        return JsonResponse({"error": str(exc)}, status=503)

    return JsonResponse(
        {"id": str(test.id), "subject": test.subject, "rank": test.rank}, status=201
    )


@login_required
def complete_diagnostic_test(request, test_id):
    if request.method != "POST":
        raise Http404()

    test = get_object_or_404(
        DiagnosticTest.objects.select_related("child"),
        id=test_id,
        child__parent=request.user,
    )

    if not test.is_completed:
        try:
            services.score_test_from_responses(test)
        except ValidationError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        test.refresh_from_db()

    return JsonResponse({"rank": test.rank})
