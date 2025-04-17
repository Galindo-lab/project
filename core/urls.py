from django import views
from django.conf.urls.static import static
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views

from project import settings

from core.views import index
from core.views import register

urlpatterns = [
    path("", index, name="home"),
    
    # Login
    path('login/', auth_views.LoginView.as_view(template_name='view/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    
    # URLs para la pwa
    path('', include('pwa.urls')),
]
