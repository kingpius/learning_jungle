from django import forms

from .models import Child


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ["first_name", "age", "school_name", "year_group"]
