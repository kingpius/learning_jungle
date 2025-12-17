from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("start/<uuid:child_id>/", views.diagnostic_start, name="diagnostic_start"),
    path(
        "questions/<uuid:test_id>/",
        views.diagnostic_questions,
        name="diagnostic_questions",
    ),
    path("results/<uuid:test_id>/", views.diagnostic_results, name="diagnostic_results"),
    path(
        "api/tests/<uuid:child_id>/",
        views.create_diagnostic_test,
        name="create_diagnostic_test",
    ),
    path(
        "api/tests/<uuid:test_id>/complete/",
        views.complete_diagnostic_test,
        name="complete_diagnostic_test",
    ),
]
