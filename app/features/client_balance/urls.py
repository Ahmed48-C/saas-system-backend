from django.urls import path
from app.features.client_balance.views import (
    get_all_client_balance,
)

urlpatterns = [
    path('get/client_balances/', get_all_client_balance),
]