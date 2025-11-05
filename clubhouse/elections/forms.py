# File: elections/forms.py
from django import forms
from django.contrib.auth.models import User

from .models import Election
from django.utils import timezone

DATETIME_FMT = '%Y-%m-%dT%H:%M'

class ElectionForm(forms.ModelForm):
    # Use native pickers via datetime-local
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format=DATETIME_FMT),
        input_formats=[DATETIME_FMT]
    )
    end_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format=DATETIME_FMT),
        input_formats=[DATETIME_FMT]
    )

    class Meta:
        model = Election
        fields = ['start_at', 'end_at']

    def clean(self):
        data = super().clean()
        s = data.get('start_at')
        e = data.get('end_at')
        # Must end after start
        if s and e and e <= s:
            raise forms.ValidationError("End must be after start.")
        # Make timezone-aware if needed
        tz = timezone.get_current_timezone()
        if s and timezone.is_naive(s):
            data['start_at'] = timezone.make_aware(s, tz)
        if e and timezone.is_naive(e):
            data['end_at'] = timezone.make_aware(e, tz)
        return data

class VoteForm(forms.Form):
    candidate = forms.ModelChoiceField(queryset=User.objects.none())
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('candidates_qs')
        super().__init__(*args, **kwargs)
        self.fields['candidate'].queryset = qs
