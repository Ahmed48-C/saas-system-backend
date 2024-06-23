from django.urls import path
from app.views import (
    records_list,
    get_all_location,
    create_location,
)

urlpatterns = [
    path('get/records/', records_list),
    path('get/locations/', get_all_location),
    path('post/location/', create_location),
]