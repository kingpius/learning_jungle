from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("design-system/", views.design_system, name="design-system"),
    path("design-system/elements/", views.design_system_elements, name="design-system-elements"),
]
