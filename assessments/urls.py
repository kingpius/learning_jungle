from django.urls import path

from .views import create_diagnostic_test, complete_diagnostic_test

app_name = "assessments"

urlpatterns = [
    path(
        "children/<uuid:child_id>/tests/",
        create_diagnostic_test,
        name="create_diagnostic_test",
    ),
    path(
        "tests/<uuid:test_id>/complete/",
        complete_diagnostic_test,
        name="complete_diagnostic_test",
    ),
]
