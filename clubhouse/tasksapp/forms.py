# File: tasksapp/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Task

class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True, profile__is_approved=True),
        required=False, help_text="Assign members to this task"
    )
    class Meta:
        model = Task
        fields = ['title', 'description', 'week_start', 'due_at', 'assignees']
        widgets = {
            'week_start': forms.DateInput(attrs={'type': 'date'}),
            'due_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
