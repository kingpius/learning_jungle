from django.urls import path
from .views import create_treasure_chest

app_name = "rewards"

urlpatterns = [
    path("create/<int:child_id>/", create_treasure_chest, name="create"),
]
