from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class AccountType(models.TextChoices):
        BASIC = "basic", "Basic"
        PREMIUM = "premium", "Premium"

    account_type = models.CharField(max_length=10, choices=AccountType.choices)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.account_type


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creation_date = models.DateTimeField()
    last_modified = models.DateTimeField()
    is_archived = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def calculate_total_cost(self):
        total_cost = 0
        for goal in self.goal_set.all():
            for task in goal.task_set.all():
                for resource in task.resources.all():
                    total_cost += resource.cost_per_hour * task.duration_hours
        return total_cost 


    def __str__(self):
        return self.name


class Collaborator(models.Model):
    role = models.CharField(max_length=50)
    invitation_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Goal(models.Model):  # formerly "Meta"
    name = models.CharField(max_length=100)
    description = models.TextField()
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=0.0)
    order = models.IntegerField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.order is None:
            last_goal = Goal.objects.filter(project=self.project).order_by('-order').first()
            if last_goal:
                self.order = last_goal.order + 1
            else:
                self.order = 0
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_hours = models.IntegerField() 
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices)
    creation_date = models.DateTimeField(auto_now_add=True)  
    update_date = models.DateTimeField(auto_now=True) 
    goal = models.ForeignKey("Goal", on_delete=models.CASCADE)
    dependencies = models.ManyToManyField("self", symmetrical=False, blank=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        HUMAN = "human", "Human"
        MATERIAL = "material", "Material"
        FINANCIAL = "financial", "Financial"
        TECHNOLOGICAL = "technological", "Technological"

    name = models.CharField(max_length=100)
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=ResourceType.choices)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tasks = models.ManyToManyField(Task, related_name="resources")

    def __str__(self):
        return self.name
