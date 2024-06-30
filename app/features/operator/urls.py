from django.urls import path
from app.features.operator.views import (
    get_all_operator,
    create_operator,
    update_operator,
    delete_operator,
    get_operator_by_id,
)

urlpatterns = [
    path('get/operator/<operator_id>/', get_operator_by_id),
    path('get/operators/', get_all_operator),
    path('post/operator/', create_operator),
    path('put/operator/<operator_id>/', update_operator),
    path('delete/operator/<operator_id>/', delete_operator),
]