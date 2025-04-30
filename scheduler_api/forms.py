from django import forms
from .models import Interview
from datetime import datetime, time
from django.utils import timezone
import zoneinfo

# creates a form to initiate scheduling by client/Interviewer
class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['candidate','date', 'time', 'time_zone']
        widgets = {
            'date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'time': forms.TimeInput(attrs={'class':'form-control', 'type':'time'})
        }

       