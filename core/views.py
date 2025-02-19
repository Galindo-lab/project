from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from core.forms import UbicacionForm
from core.models import Ubicacion


        
        
class UbicacionCreateView(CreateView):
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'a.html'
    success_url = reverse_lazy('ubicacion')