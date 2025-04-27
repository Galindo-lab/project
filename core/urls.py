from django import views
from django.conf.urls.static import static
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views

from project import settings

from core.views import DeleteProjectView, ProjectEditView, index
from core.views import register, ProjectListView, ProjectCreateView, ArchiveProjectView, GoalsListView

urlpatterns = [
    path("home/", ProjectListView.as_view(), name="home"),
    
    # proyect
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('project/update/', ProjectEditView.as_view(), name='update_project'),
    path('project/delete/', DeleteProjectView.as_view(), name='delete_project'),
    path('project/archive/', ArchiveProjectView.as_view(), name='archive_project'),
    
    path('project/<int:pk>/', GoalsListView.as_view(), name='list_goals'),
    
    # Login
    path('login/', auth_views.LoginView.as_view(template_name='view/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    
    # URLs para el restablecimiento de contraseña
    path(route='reset_password/', view=auth_views.PasswordResetView.as_view(
        template_name='view/password/reset.html'), name='reset_password'),

    path(route='reset_password_sent/', view=auth_views.PasswordResetDoneView.as_view(
        template_name='view/password/resetDone.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='view/password/resetConfirm.html'), name='password_reset_confirm'),

    path(route='reset_password_complete/', view=auth_views.PasswordResetCompleteView.as_view(
        template_name='view/password/complete.html'), name='password_reset_complete'),
    
    # URLs para la pwa
    path('', include('pwa.urls')),
]
