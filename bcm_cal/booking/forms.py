from django import forms

class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.HiddenInput())
    time_slot = forms.TimeField(widget=forms.HiddenInput())

