from django.conf.urls.static import static
from django.urls import path
from django.urls import include

from project import settings

urlpatterns = [
    
    # URLs para la pwa
    path('', include('pwa.urls')),
]
