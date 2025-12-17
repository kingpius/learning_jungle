from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from children.forms import ChildForm
from children.models import Child


class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = "children/child_list.html"
    context_object_name = "children"

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)


class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = ChildForm
    template_name = "children/child_form.html"
    success_url = reverse_lazy("children:list")

    def form_valid(self, form):
        form.instance.parent = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Child profile created.")
        return response


class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildForm
    template_name = "children/child_form.html"
    success_url = reverse_lazy("children:list")

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Child profile updated.")
        return response


class ChildDeleteView(LoginRequiredMixin, DeleteView):
    model = Child
    template_name = "children/child_confirm_delete.html"
    success_url = reverse_lazy("children:list")

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Child profile deleted.")
        return super().form_valid(form)
