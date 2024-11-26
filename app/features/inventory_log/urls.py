from django.urls import path
from app.features.inventory_log.views import (
    get_all_inventory_log,
    create_inventory_log,
    update_inventory_log,
    delete_inventory_log,
    get_inventory_log_by_id,
    delete_inventory_logs,
)

urlpatterns = [
    # path('get/inventory_log/<inventory_log_id>/', get_inventory_log_by_id),
    path('get/inventory_logs/', get_all_inventory_log),
    # path('post/inventory_log/', create_inventory_log),
    # path('put/inventory_log/<inventory_log_id>/', update_inventory_log),
    path('delete/inventory_log/<inventory_log_id>/', delete_inventory_log),
    path('delete/inventory_logs/', delete_inventory_logs),
]