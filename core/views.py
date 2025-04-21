import json

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone

from django.shortcuts import redirect, render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.forms import ProjectForm, RegisterForm
from core.models import Project


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
        # Si el formulario no es válido, se renderiza con los errores
    else:
        form = RegisterForm()  # Formulario vacío para GET requests

    return render(
        request,
        "view/register.html",
        {"form": form},  # Pasa el formulario con errores si los hay
    )


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ["name", "description", "is_archived"]
    success_url = reverse_lazy("home")  # URL a donde redirigir

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.creation_date = timezone.now()
        form.instance.last_modified = timezone.now()

        project_name = form.cleaned_data.get("name", "nuevo proyecto")
        messages.success(
            self.request, f"Proyecto '{project_name}' creado correctamente!"
        )

        return super().form_valid(form)

    def form_invalid(self, form):

        # Mensajes detallados por cada campo con error
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"Campo '{form.fields[field].label}' es obligatorio."
                )

        return redirect(self.success_url)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "view/proyectList.html"
    context_object_name = "projects"
    ordering = ["-last_modified"]
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()

        # Filtrar por archivo si no se solicita mostrar archivados
        if not self.request.GET.get("show_archived"):
            queryset = queryset.filter(is_archived=False)

        # Aplicar búsqueda si hay un término de búsqueda
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(created_by__username__icontains=search_query)
            )

        return queryset.select_related("created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_archived"] = (
            self.request.GET.get("show_archived", "false").lower() == "true"
        )
        context["search_query"] = self.request.GET.get('search', '')
        return context