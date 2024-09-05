from django.urls import path
from app.features.balance.views import (
    get_all_balance,
    create_balance,
    update_balance,
    delete_balance,
    get_balance_by_id,
    delete_balances,
)

urlpatterns = [
    path('get/balance/<balance_id>/', get_balance_by_id),
    path('get/balances/', get_all_balance),
    path('post/balance/', create_balance),
    path('put/balance/<balance_id>/', update_balance),
    path('delete/balance/<balance_id>/', delete_balance),
    path('delete/balances/', delete_balances),
]