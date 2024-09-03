from django.contrib import admin

# Register your models here.
from app.features.reminder.models import Reminder

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'date',
        'time',
        'reached',
    ]
