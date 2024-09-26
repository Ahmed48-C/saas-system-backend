from django.urls import path
from app.features.transfer.views import (
    get_all_transfer,
    create_transfer,
    delete_transfer,
    get_transfer_by_id,
    delete_transfers,
)

urlpatterns = [
    path('get/transfer/<transfer_id>/', get_transfer_by_id),
    path('get/transfers/', get_all_transfer),
    path('post/transfer/', create_transfer),
    path('delete/transfer/<transfer_id>/', delete_transfer),
    path('delete/transfers/', delete_transfers),
]