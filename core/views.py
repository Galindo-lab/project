import openpyxl
import csv
from urllib.parse import urlencode
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
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

from .forms import ArchiveProjectForm, CreateResourceForm, CreateTaskForm, ProjectEditForm, RegisterForm, TaskEditForm
from .models import Collaborator, Goal, Project, Resource, Task
from .generators import GeminiGenerator



class UserListView(ListView):
    model = User
    template_name = 'view/userList/main.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        return queryset

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.is_active = False
        user.save()
        messages.success(request, "Usuario deshabilitado correctamente.")
        return redirect('user_list')
    return render(request, 'view/userList/modal/deleteUser.html', {'user': user})

@login_required
def index(request):
    """
    Render the index page.
    """
    return render(request, "layout/app/main.html")



class UserEditView(UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
    template_name = 'view/userList/editUser.html'
    success_url = reverse_lazy('user_list')


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


def invitar_usuario(request, project_id):
    if request.method == 'POST':
        email = request.POST.get('email')
        project = get_object_or_404(Project, id=project_id)
        
        # Restricción para cuentas básicas
        if request.user == project.owner and getattr(request.user, "account_type", "basic") == "basic":
            # Excluye al dueño del conteo de colaboradores
            num_colaboradores = Collaborator.objects.filter(project=project).exclude(user=project.owner).count()
            if num_colaboradores >= 1:
                messages.error(request, "Con una cuenta básica solo puedes agregar un colaborador a tu proyecto.")
                return redirect('details_project', pk=project.id)
        
        try:
            user = User.objects.get(email=email)
            # Verifica si ya es colaborador
            if Collaborator.objects.filter(user=user, project=project).exists():
                messages.info(request, f"{email} ya es colaborador de este proyecto.")
            else:
                Collaborator.objects.create(
                    user=user,
                    project=project,
                    role="Colaborador",
                    invitation_date=timezone.now()
                )
                send_mail(
                    'Invitación a colaborar en un proyecto',
                    f'Has sido agregado como colaborador al proyecto "{project.name}".',
                    'no-reply@tusitio.com',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f'{email} ha sido agregado como colaborador y notificado por correo.')
        except User.DoesNotExist:
            # Usuario no registrado, solo enviar invitación
            send_mail(
                'Invitación a colaborar en un proyecto',
                f'Has sido invitado al proyecto "{project.name}". Regístrate para participar.',
                'no-reply@tusitio.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, f'Se ha enviado una invitación a {email}. Cuando se registre, podrá ser agregado como colaborador.')
        return redirect('details_project', pk=project.id)


@login_required
def eliminar_colaborador(request, project_id):
    
    if request.method != "POST":
        messages.error(request, "Operación no permitida.")
        return redirect('details_project', pk=project_id)

    collaborator_id = request.POST.get("collaborator_id")
    if not collaborator_id:
        messages.error(request, "No se especificó el colaborador a eliminar.")
        return redirect('details_project', pk=project_id)

    project = get_object_or_404(Project, id=project_id)
    collaborator = get_object_or_404(Collaborator, id=collaborator_id, project=project)

    if collaborator.user == project.owner:
        messages.error(request, "No puedes eliminar al propietario del proyecto.")
    else:
        collaborator.delete()
        messages.success(request, "Colaborador eliminado correctamente.")

    return redirect('details_project', pk=project_id)


# Vistas de Recursos
class ResourceEditView(LoginRequiredMixin, View):
    def post(self, request, project_pk, *args, **kwargs):
        resource_id = request.POST.get("resource_id")
        resource = get_object_or_404(Resource, pk=resource_id, project__pk=project_pk)

        resource.name = request.POST.get("name")
        resource.type = request.POST.get("type")
        resource.cost_per_hour = request.POST.get("cost_per_hour")
        resource.save()

        messages.success(request, "Recurso modificado correctamente!")
        return redirect(reverse("resources", kwargs={"project_pk": project_pk}))


class ResourceDeleteView(LoginRequiredMixin, View):
    def post(self, request, project_pk, *args, **kwargs):
        resource_id = request.POST.get("resource_id")
        project = get_object_or_404(Project, pk=project_pk)
        resource = get_object_or_404(Resource, pk=resource_id, project=project)

        resource.delete()
        messages.success(request, "Recurso eliminado correctamente!")
        return redirect(reverse("resources", kwargs={"project_pk": project.pk}))


class ResourceCreateView(LoginRequiredMixin, View):
    def post(self, request, project_pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        
        # URL de redirección
        redirect_url = reverse("resources", kwargs={"project_pk": project.pk})
        
        resource_form = CreateResourceForm(request.POST)
        if resource_form.is_valid():
            resource = resource_form.save(commit=False)
            resource.project = project
            resource.save()
            messages.success(request, "Recurso creado correctamente!")
            return redirect(redirect_url)
        
        messages.error(request, "Error al crear el recurso. Por favor, verifica los datos ingresados.")
        return redirect(redirect_url)
    

class ResourcesListView(LoginRequiredMixin, ListView):
    model = Resource
    template_name = "view/resourcesList/main.html"
    context_object_name = "resources"
    paginate_by = 10

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        search_query = self.request.GET.get("search", "").strip()

        if search_query:
            return project.resource_set.filter(
                Q(name__icontains=search_query)
            )

        return project.resource_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["project"] = project
        context["resource_type_choices"] = Resource.ResourceType.choices  # Agregar las opciones de tipo de recurso
        return context
    

# Vistas de Tareas
class TaskDetailView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskEditForm
    template_name = "view/taskDetails.html"

    def get_object(self):
        task_id = self.kwargs.get("task_pk")
        return get_object_or_404(Task, pk=task_id)

    def get_success_url(self):
        task = self.get_object()
        return reverse("details_task", kwargs={"task_pk": task.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        goal = get_object_or_404(Goal, pk=task.goal.pk)
        project = get_object_or_404(Project, pk=goal.project.pk)
        context["project"] = project
        return context

    def form_valid(self, form):
        messages.success(self.request, "¡Tarea actualizada correctamente!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error en {form.fields[field].label}: {error}")
        return super().form_invalid(form)
    
    
class TaskCreateView(LoginRequiredMixin, View):
    def post(self, request, goal_pk, *args, **kwargs):
        goal = get_object_or_404(Goal, pk=goal_pk)
        project = get_object_or_404(Project, pk=goal.project.pk)
        redirect_url = reverse("list_goals", kwargs={"pk": project.pk}) + f"?goal_pk={goal_pk}"

        task_form = CreateTaskForm(request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.goal = goal
            task.save()
            task_form.save_m2m()  # Guarda los recursos seleccionados
            messages.success(request, "Tarea creada correctamente!")
            return redirect(redirect_url)
        
        messages.error(request, "Error al crear la tarea.")
        return redirect(redirect_url)
        
        
class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get("task_id")
        task = get_object_or_404(Task, pk=task_id)
        goal = get_object_or_404(Goal, pk=task.goal.pk)
        project = get_object_or_404(Project, pk=goal.project.pk)
        
        # url de redirección
        redirect_url = reverse("list_goals", kwargs={"pk": project.pk})
        # si hay un goal_pk en la url, lo añadimos como parámetro
        redirect_url += f"?goal_pk={goal.pk}"
        
        task.delete()
        messages.success(request, "Tarea eliminada correctamente!")
        return redirect(redirect_url)


# Vistas de Objetivos
class GoalsListView(LoginRequiredMixin, ListView):
    template_name = "view/goalList/main.html"
    context_object_name = "goals"
    paginate_by = 10

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        search_query = self.request.GET.get("search", "").strip()
        get_goal_pk = self.request.GET.get("goal_pk")

        if get_goal_pk and get_goal_pk != "":
            queryset = self.project.goal_set.filter(pk=get_goal_pk)
        else:
            queryset = Goal.objects.filter(project=self.project).order_by("order")

        if search_query:
            # Filtrar metas que tienen tareas que coinciden con el término de búsqueda
            queryset = queryset.filter(
                task__name__icontains=search_query
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        context["search_query"] = self.request.GET.get("search", "")

        # Filtrar las tareas de cada meta según el término de búsqueda
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            for goal in context["goals"]:
                goal.filtered_tasks = goal.task_set.filter(name__icontains=search_query)
        else:
            for goal in context["goals"]:
                goal.filtered_tasks = goal.task_set.all()

        return context


class GoalOrderView(LoginRequiredMixin, View):
    def get(self, request, pk, goalpk, action):
        current_goal = get_object_or_404(Goal, pk=goalpk, project__pk=pk)
        
        # Obtenemos todos los objetivos ordenados del proyecto
        goals = list(Goal.objects.filter(project=current_goal.project).order_by('order'))
        current_index = next((i for i, g in enumerate(goals) if g.pk == current_goal.pk), None)

        with transaction.atomic():
            if action == "up":
                self._move_up(current_goal, goals, current_index, request)
            elif action == "down":
                self._move_down(current_goal, goals, current_index, request)
            else:
                messages.error(request, "Acción no válida o movimiento imposible.")

        return redirect(reverse("list_goals", kwargs={"pk": pk}))

    def _move_up(self, current_goal, goals, current_index, request):
        if current_index > 0:
            # Intercambiar con el anterior
            previous_goal = goals[current_index - 1]
            current_goal.order, previous_goal.order = previous_goal.order, current_goal.order
            current_goal.save()
            previous_goal.save()
        else:
            messages.error(request, "No se puede subir más.")

    def _move_down(self, current_goal, goals, current_index, request):
        if current_index < len(goals) - 1:
            # Intercambiar con el siguiente
            next_goal = goals[current_index + 1]
            current_goal.order, next_goal.order = next_goal.order, current_goal.order
            current_goal.save()
            next_goal.save()
        else:
            messages.error(request, "No se puede bajar más.")


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
    def get(self, request, pk, goalpk, *args, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        goal = get_object_or_404(Goal, pk=goalpk, project=project)

        gg = GeminiGenerator()
        goal2 = gg.generate_goal(project, project.description, goalpk)
        
        print(goal2)

        goal.name = goal2.name
        goal.description = goal2.description
        goal.save()

        messages.success(request, "Contenido generado correctamente!")
        return redirect(f"{reverse('list_goals', kwargs={'pk': pk})}?goal_pk={goal.pk}")


# Vistas de Proyecto
@login_required
def export_project_excel(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Proyecto"

    # Encabezados
    headers = ['Meta', 'Tarea', 'Duración (h)', 'Recurso(s)']
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        ws[f"{get_column_letter(col)}1"].font = Font(bold=True)

    row_num = 2
    for goal in project.goal_set.all().order_by('order'):
        if goal.task_set.exists():
            for task in goal.task_set.all():
                recursos = ', '.join([res.name for res in task.resources.all()])
                ws.append([
                    goal.name,
                    task.name,
                    task.duration_hours,
                    recursos
                ])
                row_num += 1
        else:
            ws.append([goal.name, '', '', ''])
            row_num += 1

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass
        ws.column_dimensions[column].width = max_length + 2

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="proyecto_{project.id}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_project_csv(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="proyecto_{project.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Meta', 'Tarea', 'Duración (h)', 'Recurso(s)'])

    for goal in project.goal_set.all().order_by('order'):
        for task in goal.task_set.all():
            recursos = ', '.join([res.name for res in task.resources.all()])
            writer.writerow([
                goal.name,
                task.name,
                task.duration_hours,
                recursos
            ])
        # Si una meta no tiene tareas, igual la mostramos
        if not goal.task_set.exists():
            writer.writerow([goal.name, '', '', ''])

    return response


class ProjectEditView(LoginRequiredMixin, View):
    template_name = "view/projectDetails/main.html"

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
