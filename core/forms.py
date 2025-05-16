from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Goal, Project, Task, Resource
from django.utils import timezone




class EmprendedorDescripcionForm(forms.Form):
    idea = forms.CharField(label="¿Cuál es tu idea de negocio o proyecto?", widget=forms.Textarea)
    experiencia = forms.CharField(label="¿Cuál es tu nivel de experiencia en este sector?", widget=forms.Textarea)
    implementado = forms.CharField(label="¿Qué tienes implementado hasta ahora?", widget=forms.Textarea)
    objetivo = forms.CharField(label="¿Cuál es tu objetivo principal con este proyecto?", widget=forms.Textarea)
    publico = forms.CharField(label="¿A quién va dirigido tu proyecto?", widget=forms.Textarea)
    problema = forms.CharField(label="¿Qué problema resuelve tu proyecto?", widget=forms.Textarea)
    solucion = forms.CharField(label="¿Cómo soluciona ese problema?", widget=forms.Textarea)
    diferenciador = forms.CharField(label="¿Qué hace diferente a tu proyecto de otros?", widget=forms.Textarea)
    recursos = forms.CharField(label="¿Con qué recursos cuentas actualmente?", widget=forms.Textarea)
    proximo_paso = forms.CharField(label="¿Cuál es el siguiente paso que planeas dar?", widget=forms.Textarea)

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "duration_hours", "status", "priority", "resources", "predecessor"]
        widgets = {
            "resources": forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),

            "predecessor": forms.Select,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance and instance.goal:
            self.fields["predecessor"].queryset = Task.objects.filter(goal=instance.goal).exclude(pk=instance.pk)


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'duration_hours']

class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

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


class CreateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["name", "type", "cost_per_hour"]
