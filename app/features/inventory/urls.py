from django.urls import path
from app.features.inventory.views import (
    get_all_inventory,
    create_inventory,
    update_inventory,
    delete_inventory,
    get_inventory_by_id,
    delete_inventories,
)

urlpatterns = [
    path('get/inventory/<inventory_id>/', get_inventory_by_id),
    path('get/inventories/', get_all_inventory),
    path('post/inventory/', create_inventory),
    path('put/inventory/<inventory_id>/', update_inventory),
    path('delete/inventory/<inventory_id>/', delete_inventory),
    path('delete/inventories/', delete_inventories),
]