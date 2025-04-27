from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.models import Goal, Project

from django.utils import timezone


class ArchiveProjectForm(forms.Form):
    project_id = forms.IntegerField(widget=forms.HiddenInput())

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'description', 'project']
        
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.creation_date = timezone.now()
        instance.last_modified = timezone.now()
        if commit:
            instance.save()
        return instance


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
