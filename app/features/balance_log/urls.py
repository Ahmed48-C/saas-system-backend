from django.urls import path
from app.features.balance_log.views import (
    get_all_balance_log,
    create_balance_log,
    update_balance_log,
    delete_balance_log,
    get_balance_log_by_id,
    delete_balance_logs,
)

urlpatterns = [
    path('get/balance_log/<balance_log_id>/', get_balance_log_by_id),
    path('get/balance_logs/', get_all_balance_log),
    path('post/balance_log/', create_balance_log),
    path('put/balance_log/<balance_log_id>/', update_balance_log),
    path('delete/balance_log/<balance_log_id>/', delete_balance_log),
    path('delete/balance_logs/', delete_balance_logs),
]