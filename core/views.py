import json

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.forms import RegisterForm

def index(request):
    """
    Render the index page.
    """
    return render(request, 'layout/app.html')

from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        # Si el formulario no es válido, se renderiza con los errores
    else:
        form = RegisterForm()  # Formulario vacío para GET requests
    
    return render(request, 'view/register.html', {
        'form': form  # Pasa el formulario con errores si los hay
    })