from django import views
from django.conf.urls.static import static
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views

from project import settings

from core.views import index
from core.views import register

urlpatterns = [
    path("home/", index, name="home"),
    
    # Login
    path('login/', auth_views.LoginView.as_view(template_name='view/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    
    # URLs para el restablecimiento de contraseña
    path(route='reset_password/', view=auth_views.PasswordResetView.as_view(
        template_name='view/reset.html'), name='reset_password'),

    path(route='reset_password_sent/', view=auth_views.PasswordResetDoneView.as_view(
        template_name='view/resetDone.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='view/resetConfirm.html'), name='password_reset_confirm'),

    path(route='reset_password_complete/', view=auth_views.PasswordResetCompleteView.as_view(
        template_name='view/resetComplete.html'), name='password_reset_complete'),
    
    # URLs para la pwa
    path('', include('pwa.urls')),
]
