from django.urls import path
from app.features.supplier.views import (
    get_all_supplier,
    create_supplier,
    update_supplier,
    delete_supplier,
    get_supplier_by_id,
    delete_suppliers,
)

urlpatterns = [
    path('get/supplier/<supplier_id>/', get_supplier_by_id),
    path('get/suppliers/', get_all_supplier),
    path('post/supplier/', create_supplier),
    path('put/supplier/<supplier_id>/', update_supplier),
    path('delete/supplier/<supplier_id>/', delete_supplier),
    path('delete/suppliers/', delete_suppliers),
]