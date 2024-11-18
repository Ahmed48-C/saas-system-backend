from django.urls import path
from app.features.client.views import (
    get_all_client,
    create_client,
    update_client,
    delete_client,
    get_client_by_id,
)

urlpatterns = [
    path('get/client/<client_id>/', get_client_by_id),
    path('get/clients/', get_all_client),
    path('post/client/', create_client),
    path('put/client/<client_id>/', update_client),
    path('delete/client/<client_id>/', delete_client),
]