from django.urls import path
from app.features.sales_order.views import (
    get_all_sales_orders,
    get_sales_order_by_id,
    create_sales_order,
    update_sales_order,
    delete_sales_orders,
    delete_sales_order,
    get_completed_sales_orders,
    get_sales_status_choices,
    get_delivery_sales_orders,
)

urlpatterns = [
    path('get/sales_order/<sales_order_id>/', get_sales_order_by_id),
    path('get/sales_orders/', get_all_sales_orders),
    path('get/completed_sales_orders/', get_completed_sales_orders),  # New endpoint
    path('get/delivery_sales_orders/', get_delivery_sales_orders),
    path('post/sales_order/', create_sales_order),
    path('put/sales_order/<sales_order_id>/', update_sales_order),
    path('delete/sales_orders/', delete_sales_orders),
    path('delete/sales_order/<sales_order_id>/', delete_sales_order),
    path('get/sales_status/', get_sales_status_choices),
]