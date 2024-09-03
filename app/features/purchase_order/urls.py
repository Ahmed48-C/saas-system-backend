from django.urls import path
from app.features.purchase_order.views import (
    get_all_purchase_order,
    create_purchase_order,
    update_purchase_order,
    delete_purchase_order,
    delete_purchase_order_stock,
    get_purchase_order_by_id,
    delete_purchase_orders,
)

urlpatterns = [
    path('get/purchase_order/<purchase_order_id>/', get_purchase_order_by_id),
    path('get/purchase_orders/', get_all_purchase_order),
    path('post/purchase_order/', create_purchase_order),
    path('put/purchase_order/<purchase_order_id>/', update_purchase_order),
    path('delete/purchase_order/<purchase_order_id>/', delete_purchase_order),
    path('delete/purchase_order_stock/<purchase_order_id>/', delete_purchase_order_stock),
    path('delete/purchase_orders/', delete_purchase_orders),
]