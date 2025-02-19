from django.conf.urls.static import static
from django.urls import path

from core.views import UbicacionCreateView
from project import settings

urlpatterns = [
    path(route='test/', view=UbicacionCreateView.as_view(), name='ubicacion'),
]