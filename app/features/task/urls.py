from django.urls import path
from app.features.task.views import (
    get_all_task,
    create_task,
    delete_task,
    update_task,
    get_task_by_id,
    get_task_status_choices,
    get_task_priority_choices,
)

urlpatterns = [
    path('get/task/<task_id>/', get_task_by_id),
    path('get/tasks/', get_all_task),
    path('post/task/', create_task),
    path('delete/task/<task_id>/', delete_task),
    path('put/task/<task_id>/', update_task),
    path('get/tasks_status/', get_task_status_choices),
    path('get/tasks_priority/', get_task_priority_choices),
]