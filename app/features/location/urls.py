from django.urls import path
from app.features.location.views import (
    records_list,
    get_all_location,
    create_location,
    update_location,
    delete_location,
    get_location_by_id,
)

urlpatterns = [
    path('get/records/', records_list),
    path('get/location/<location_id>/', get_location_by_id),
    path('get/locations/', get_all_location),
    path('post/location/', create_location),
    path('put/location/<location_id>/', update_location),
    path('delete/location/<location_id>/', delete_location),
]