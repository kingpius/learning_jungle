from django.contrib import admin

from .models import DiagnosticTest


@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display = (
        "child",
        "subject",
        "total_questions",
        "correct_answers",
        "score_percentage",
        "is_completed",
        "completed_at",
        "created_at",
    )
    list_filter = ("subject", "is_completed")
    search_fields = ("child__first_name", "child__parent__email")
