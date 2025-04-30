from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ArchiveProjectForm, ProjectEditForm, RegisterForm
from .models import Goal, Project
from .llmshet import GeminiShet, GeminiGenerator


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


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    fields = ["name", "description"]

    def get_object(self):
        goal_id = self.request.POST.get("id")
        project_id = self.kwargs.get("pk")
        return get_object_or_404(Goal, pk=goal_id, project__id=project_id)

    def get_success_url(self):
        return reverse("list_goals", kwargs={"pk": self.kwargs.get("pk")})

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Meta '{form.cleaned_data.get('name')}' actualizada correctamente!",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"Error en {form.fields[field].label}: {error}"
                )
        return redirect(self.get_success_url())


class GoalDeleteView(LoginRequiredMixin, View):
    """
    Vista para eliminar una meta (Goal).
    La URL incluye el project_id como pk y el goal_id debe venir por POST.
    """

    def post(self, request, pk, *args, **kwargs):
        try:
            goal_id = request.POST.get("goal_id")

            if not goal_id:
                messages.error(request, "Falta el ID de la meta a eliminar.")
                return redirect("home")

            project = get_object_or_404(Project, id=pk)
            goal = get_object_or_404(Goal, id=goal_id, project=project)

            goal.delete()

            messages.success(request, "¡Meta eliminada correctamente!")
        except Exception as e:
            messages.error(request, f"Error al eliminar la meta: {str(e)}")

        return redirect(reverse("list_goals", kwargs={"pk": pk}))


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    fields = ["name", "description"]

    def get_success_url(self):
        return reverse("list_goals", kwargs={"pk": self.kwargs.get("pk")})

    def form_valid(self, form):
        # Asignar automáticamente el proyecto desde la URL
        project = get_object_or_404(Project, pk=self.kwargs.get("pk"))
        form.instance.project = project

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

        return redirect(reverse("list_goals", kwargs={"pk": self.kwargs.get("pk")}))

class GoalGenerateView(LoginRequiredMixin, View):
    def get(self, request, pk, goalpk):
        project = get_object_or_404(Project, pk=pk)
        goal = get_object_or_404(Goal, pk=goalpk, project=project)

        # Generar el contenido de la meta utilizando GeminiShet
        generator = GeminiGenerator()
        goal2 = generator.generate_goal(project, project.description, goalpk)
        
        goal.name = goal2.name
        goal.description = goal2.description
        
        goal.save()

        messages.success(request, "Contenido generado correctamente!")
        return redirect(reverse("list_goals", kwargs={"pk": pk}))

# Vistas de Proyecto
class ProjectEditView(LoginRequiredMixin, View):
    template_name = "view/proyectDetails.html"

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        form = ProjectEditForm(instance=project)
        context = {"form": form, "project": project}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        form = ProjectEditForm(request.POST, instance=project)

        if form.is_valid():
            project = form.save(commit=False)
            project.last_modified = timezone.now()
            project.save()
            messages.success(request, "Proyecto actualizado correctamente")

        context = {"form": form, "project": project}
        return render(request, self.template_name, context)


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
