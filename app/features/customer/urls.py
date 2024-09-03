from django.urls import path
from app.features.customer.views import (
    get_all_customer,
    create_customer,
    update_customer,
    delete_customer,
    get_customer_by_id,
    delete_customers,
)

urlpatterns = [
    path('get/customer/<customer_id>/', get_customer_by_id),
    path('get/customers/', get_all_customer),
    path('post/customer/', create_customer),
    path('put/customer/<customer_id>/', update_customer),
    path('delete/customer/<customer_id>/', delete_customer),
    path('delete/customers/', delete_customers),
]