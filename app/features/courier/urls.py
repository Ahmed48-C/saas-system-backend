from django.urls import path
from app.features.courier.views import (
    get_all_courier,
    create_courier,
    update_courier,
    delete_courier,
    get_courier_by_id,
)

urlpatterns = [
    path('get/courier/<courier_id>/', get_courier_by_id),
    path('get/couriers/', get_all_courier),
    path('post/courier/', create_courier),
    path('put/courier/<courier_id>/', update_courier),
    path('delete/courier/<courier_id>/', delete_courier),
]