import json
from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.utils import timezone

from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.forms import ArchiveProjectForm, GoalForm, RegisterForm
from core.models import Goal, Project


@login_required
def index(request):
    """
    Render the index page.
    """
    return render(request, "layout/app/main.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "view/register.html",
        {"form": form},
    )


# Vistas de Objetivos
class GoalsListView(LoginRequiredMixin, ListView):
    template_name = "view/goalList/main.html"
    context_object_name = "goals"
    paginate_by = 10

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])

        get_goal_pk = self.request.GET.get("goal_pk")
        if get_goal_pk and get_goal_pk != "":
            return self.project.goal_set.filter(pk=get_goal_pk)

        return Goal.objects.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    fields = ["name", "description", "project", "completion_percentage"]

    def get_success_url(self):
        return reverse("list_goals", kwargs={"pk": self.request.POST.get("project")})

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Meta '{form.cleaned_data.get('name', 'nuevo objetivo')}' creado correctamente!",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"Error en {form.fields[field].label}: {error}"
                )

        return redirect(
            reverse("list_goals", kwargs={"pk": self.request.POST.get("project")})
        )


# Vistas de Proyecto


class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ["name", "description", "is_archived"]
    template_name = "view/proyectEdit/main.html"
    success_url = reverse_lazy("home")

    def get_object(self, queryset=None):
        project = super().get_object(queryset)
        if self.request.user != project.owner:
            raise PermissionDenied("No tienes permiso para editar este proyecto")
        return project

    def form_valid(self, form):
        form.instance.last_modified = timezone.now()

        project_name = form.cleaned_data.get("name", "proyecto")
        messages.success(
            self.request, f"Proyecto '{project_name}' actualizado correctamente!"
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"Error en '{form.fields[field].label}': {error}"
                )
        return super().form_invalid(form)


class DeleteProjectView(LoginRequiredMixin, FormView):
    form_class = ArchiveProjectForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        project_id = form.cleaned_data["project_id"]
        project = get_object_or_404(Project, pk=project_id)

        if self.request.user == project.owner:
            project.delete()
            messages.success(self.request, "Proyecto eliminado correctamente")
        else:
            messages.error(
                self.request, "No tienes permiso para eliminar este proyecto"
            )
            return self.form_invalid(form)

        return super().form_valid(form)


class ArchiveProjectView(LoginRequiredMixin, FormView):
    form_class = ArchiveProjectForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        project_id = form.cleaned_data["project_id"]
        try:
            project = Project.objects.get(pk=project_id)
            project.is_archived = True
            project.save()

            messages.success(self.request, f"Proyecto archivado correctamente!")

        except Project.DoesNotExist:
            messages.error(self.request, f"Campo es obligatorio.")
            pass

        return super().form_valid(form)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ["name", "description", "is_archived"]
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.creation_date = timezone.now()
        form.instance.last_modified = timezone.now()

        project_name = form.cleaned_data.get("name", "nuevo proyecto")
        messages.success(
            self.request, f"Proyecto '{project_name}' creado correctamente!"
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"Campo '{form.fields[field].label}' es obligatorio."
                )

        return redirect(self.success_url)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "view/proyectList/main.html"
    context_object_name = "projects"
    ordering = ["-last_modified"]
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        search_query = self.request.GET.get("search", "").strip()

        if self.request.GET.get("filter") == "archived":
            queryset = queryset.filter(is_archived=True)

        if self.request.GET.get("filter") == "active":
            queryset = queryset.filter(is_archived=False)

        # Aplicar búsqueda si hay un término de búsqueda
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(owner__username__icontains=search_query)
            )

        return queryset.select_related("owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        if "page" in query_params:
            del query_params["page"]
        context["current_query"] = urlencode(query_params)
        context["search_query"] = self.request.GET.get("search", "")
        context["current_filter"] = self.request.GET.get("filter", "")
        return context
