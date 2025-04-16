from django.conf.urls.static import static
from django.urls import path
from django.urls import include

from core.views import UbicacionCreateView
from core.views import recibir_ubicacion
from core.views import index
from project import settings

urlpatterns = [
    path('', index, name='index'),
    path(route="test/", view=UbicacionCreateView.as_view(), name="ubicacion"),
    path('recibir-ubicacion/', recibir_ubicacion, name='recibir_ubicacion'),

    # URLs para la pwa
    path('', include('pwa.urls')),
]
