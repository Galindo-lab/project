import json

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.forms import UbicacionForm
from core.models import Ubicacion

def index(request):
    return render(request, 'index.html')


class UbicacionCreateView(CreateView):
    model = Ubicacion
    form_class = UbicacionForm
    template_name = "a.html"
    success_url = reverse_lazy("ubicacion")



@csrf_exempt
def recibir_ubicacion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitud = data.get('latitud')
        longitud = data.get('longitud')

        if latitud and longitud:
            print(f'\n Latitud: {latitud}, Longitud: {longitud} \n')
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)