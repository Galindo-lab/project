from django.conf.urls.static import static
from django.urls import path
from django.urls import include

from project import settings

from core.views import index

urlpatterns = [
    path("", index, name="index"),
    
    # URLs para la pwa
    path('', include('pwa.urls')),
]
