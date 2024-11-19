from django.urls import path
from app.features.courier.views import (
    get_all_courier,
    create_courier,
    update_courier,
    delete_courier,
    get_courier_by_id,
    get_courier_vehicle_types,
    delete_couriers,
)

urlpatterns = [
    path('get/courier/<courier_id>/', get_courier_by_id),
    path('get/couriers/', get_all_courier),
    path('post/courier/', create_courier),
    path('put/courier/<courier_id>/', update_courier),
    path('delete/courier/<courier_id>/', delete_courier),
    path('delete/couriers/', delete_couriers),
    path('get/vehicle_types/', get_courier_vehicle_types),
]