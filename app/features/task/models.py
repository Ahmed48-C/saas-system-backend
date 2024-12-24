from django.db import models
from app.features.task.querymanagers import TaskQueryManager
from app.features.operator.models import Operator
# Create your models here.

class TaskStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    IN_PROGRESS = 'In Progress', 'In Progress'
    COMPLETED = 'Completed', 'Completed'
    CANCELLED = 'Cancelled', 'Cancelled'

class TaskPriority(models.TextChoices):
    LOW = 'Low', 'Low'
    MEDIUM = 'Medium', 'Medium'
    HIGH = 'High', 'High'
    URGENT = 'Urgent', 'Urgent'

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, null=True, blank=True)
    status = models.CharField(max_length=50, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    priority = models.CharField(max_length=50, choices=TaskPriority.choices, default=TaskPriority.LOW)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    objects = TaskQueryManager()

    def __str__(self):
        return self.name