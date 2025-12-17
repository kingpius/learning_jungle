from django.urls import path

from . import views

app_name = "children"

urlpatterns = [
    path("", views.ChildListView.as_view(), name="list"),
    path("create/", views.ChildCreateView.as_view(), name="create"),
    path("<uuid:pk>/edit/", views.ChildUpdateView.as_view(), name="update"),
    path("<uuid:pk>/delete/", views.ChildDeleteView.as_view(), name="delete"),
]
