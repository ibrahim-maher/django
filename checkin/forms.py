# checkin/forms.py
from django import forms
from .models import VisitorCheckIn

class CheckInForm(forms.ModelForm):
    class Meta:
        model = VisitorCheckIn
        fields = ['registration']