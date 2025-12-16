from django.contrib import admin

from .models import DiagnosticTest, DiagnosticQuestion, AIRequestLog


@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display = (
        "child",
        "subject",
        "total_questions",
        "correct_answers",
        "score_percentage",
        "rank",
        "is_completed",
        "completed_at",
        "created_at",
    )
    list_filter = ("subject", "is_completed", "rank")
    search_fields = ("child__first_name", "child__parent__email")


@admin.register(DiagnosticQuestion)
class DiagnosticQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "test",
        "order",
        "difficulty",
        "correct_option",
        "prompt_version",
    )
    list_filter = ("difficulty", "prompt_version")
    search_fields = ("test__child__first_name", "question_text")


@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "prompt_version",
        "provider",
        "status",
        "latency_ms",
        "created_at",
    )
    list_filter = ("status", "provider", "prompt_version")
