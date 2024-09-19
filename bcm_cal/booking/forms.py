from django import forms
from .models import Project


class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.HiddenInput())
    time_slot = forms.TimeField(widget=forms.HiddenInput())
    project_number = forms.IntegerField(required=False, widget=forms.HiddenInput())


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]  # Include other fields as needed
