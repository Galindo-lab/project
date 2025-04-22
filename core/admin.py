from django.contrib import admin
from django.contrib import admin
from .models import Profile, Project, Collaborator, Goal, Task, Resource

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('account_type', 'monthly_cost')
    list_filter = ('account_type',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'creation_date', 'is_archived')
    list_filter = ('is_archived',)
    search_fields = ('name', 'description')
    date_hierarchy = 'creation_date'

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'invitation_date')
    list_filter = ('role', 'invitation_date')
    search_fields = ('user__username', 'project__name')

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'priority', 'completion_percentage')
    list_filter = ('priority',)
    search_fields = ('name', 'description')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal', 'status', 'priority', 'duration_hours', 'deadline')
    list_filter = ('status', 'priority')
    search_fields = ('name', 'description')
    date_hierarchy = 'deadline'

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'project', 'cost_per_hour')
    list_filter = ('type',)
    search_fields = ('name',)
