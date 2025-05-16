from django import views
from django.conf.urls.static import static
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views

from project import settings

from core.views import (
    DeleteProjectView,
    GoalCreateView,
    GoalGenerateNewView,
    GoalOrderView,
    GoalOverwriteWithAIView,
    GoalUpdateView,
    ProjectDescriptionAICreateFormView,
    ProjectDescriptionAIEditView,
    ProjectEditView,
    ResourceEditView,
    ResourcesListView,
    TaskCreateView,
    TaskDetailView,
    TaskGenerateView,
    TaskOverwriteWithAIView,
    UserEditView,
    UserListView,
    UserProfileView,
    editar_colaborador,
    eliminar_colaborador,
    export_project_csv,
    export_project_excel,
    index,
    TaskDeleteView,
    ResourceDeleteView,
    invitar_usuario,
    user_delete,
)

from core.views import (
    register,
    ProjectListView,
    ProjectCreateView,
    ArchiveProjectView,
    GoalsListView,
    GoalDeleteView,
    ResourceCreateView,
)

urlpatterns = [
    path("home/", ProjectListView.as_view(), name="home"),
    path("perfil/", UserProfileView.as_view(), name="profile_edit"),
    path("usuarios/", UserListView.as_view(), name="user_list"),
    path("usuarios/<int:pk>/editar/", UserEditView.as_view(), name="user_edit"),
    path("usuarios/<int:pk>/eliminar/", user_delete, name="user_delete"),
    path(
        "proyecto/<int:project_id>/colaborador/<int:collaborator_id>/editar/",
        editar_colaborador,
        name="editar_colaborador",
    ),
    # proyect
    path("projects/create/", ProjectCreateView.as_view(), name="project_create"),
    path("project/delete/", DeleteProjectView.as_view(), name="delete_project"),
    path("project/archive/", ArchiveProjectView.as_view(), name="archive_project"),
    path(
        "project/<int:pk>/details/", ProjectEditView.as_view(), name="details_project"
    ),
    path("project/<int:project_id>/invite/", invitar_usuario, name="invitar_usuario"),
    path(
        "project/<int:pk>/export/excel/",
        export_project_excel,
        name="export_project_excel",
    ),
    path(
        "proyecto/<int:project_id>/colaborador/eliminar/",
        eliminar_colaborador,
        name="eliminar_colaborador",
    ),
    path(
        "project/description_ai/",
        ProjectDescriptionAICreateFormView.as_view(),
        name="project_description_ai_form",
    ),
    path(
        "project/description_ai/edit/",
        ProjectDescriptionAIEditView.as_view(),
        name="project_description_ai_edit",
    ),
    # goals
    path("project/<int:pk>/", GoalsListView.as_view(), name="list_goals"),
    path("project/<int:pk>/goal/create", GoalCreateView.as_view(), name="create_goal"),
    path("project/<int:pk>/goal/delete", GoalDeleteView.as_view(), name="delete_goal"),
    path("project/<int:pk>/goal/update", GoalUpdateView.as_view(), name="update_goal"),
    path(
        "project/<int:pk>/goal/<int:goalpk>/<str:action>",
        GoalOrderView.as_view(),
        name="order_goal",
    ),
    path(
        "project/<int:pk>/generate_goal/",
        GoalGenerateNewView.as_view(),
        name="generate_goal_new",
    ),
    path(
        "project/<int:pk>/goal/<int:goalpk>/overwrite_with_ai/",
        GoalOverwriteWithAIView.as_view(),
        name="overwrite_goal_ai",
    ),
    # tasks
    path(
        "goal/<int:goal_pk>/create/task", TaskCreateView.as_view(), name="create_task"
    ),
    path(
        "goal/<int:goal_pk>/delete/task", TaskDeleteView.as_view(), name="delete_task"
    ),
    path("task/delete/", TaskDeleteView.as_view(), name="delete_task"),
    path("task/<int:task_pk>/details/", TaskDetailView.as_view(), name="details_task"),
    path(
        "goal/<int:goal_pk>/generatetask/",
        TaskGenerateView.as_view(),
        name="generate_task",
    ),
    path(
        "task/<int:task_pk>/overwrite_with_ai/",
        TaskOverwriteWithAIView.as_view(),
        name="overwrite_task_ai",
    ),
    # resources
    path(
        "project/<int:project_pk>/resources/",
        ResourcesListView.as_view(),
        name="resources",
    ),
    path(
        "project/<int:project_pk>/resources/create",
        ResourceCreateView.as_view(),
        name="create_resource",
    ),
    path(
        "project/<int:project_pk>/resources/delete",
        ResourceDeleteView.as_view(),
        name="delete_resource",
    ),
    path(
        "project/<int:project_pk>/resources/edit",
        ResourceEditView.as_view(),
        name="edit_resource",
    ),
    # Login
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="view/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path("project/<int:pk>/export/csv/", export_project_csv, name="export_project_csv"),
    # URLs para el restablecimiento de contraseña
    path(
        route="reset_password/",
        view=auth_views.PasswordResetView.as_view(
            template_name="view/password/reset.html"
        ),
        name="reset_password",
    ),
    path(
        route="reset_password_sent/",
        view=auth_views.PasswordResetDoneView.as_view(
            template_name="view/password/resetDone.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="view/password/resetConfirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        route="reset_password_complete/",
        view=auth_views.PasswordResetCompleteView.as_view(
            template_name="view/password/complete.html"
        ),
        name="password_reset_complete",
    ),
    # URLs para la pwa
    path("", include("pwa.urls")),
]
