from django.urls import path
from app.features.reminder.views import (
    get_all_reminder,
    create_reminder,
    delete_reminder,
    update_reminder,
    get_reminder_by_id,
)

urlpatterns = [
    path('get/reminder/<reminder_id>/', get_reminder_by_id),
    path('get/reminders/', get_all_reminder),
    path('post/reminder/', create_reminder),
    path('delete/reminder/<reminder_id>/', delete_reminder),
    path('put/reminder/<reminder_id>/', update_reminder),
]