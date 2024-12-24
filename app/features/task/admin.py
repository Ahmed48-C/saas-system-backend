from django.contrib import admin

# Register your models here.
from app.features.task.models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = [
        'title',
        'description',
        'status',
        'priority',
        'created_at',
        'completed_at',
    ]
