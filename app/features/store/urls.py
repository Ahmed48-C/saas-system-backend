from django.urls import path
from app.features.store.views import (
    get_all_store,
    create_store,
    update_store,
    delete_store,
    get_store_by_id,
    delete_stores,
)

urlpatterns = [
    path('get/store/<store_id>/', get_store_by_id),
    path('get/stores/', get_all_store),
    path('post/store/', create_store),
    path('put/store/<store_id>/', update_store),
    path('delete/store/<store_id>/', delete_store),
    path('delete/stores/', delete_stores),
]