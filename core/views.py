import json

from django.shortcuts import redirect, render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from core.forms import RegisterForm

@login_required
def index(request):
    """
    Render the index page.
    """
    return render(request, 'layout/app/main.html')


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