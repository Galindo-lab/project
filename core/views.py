import json

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    """
    Render the index page.
    """
    return render(request, 'layout/app.html')


