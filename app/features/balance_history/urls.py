from django.urls import path
from app.features.balance_history.views import (
    get_all_balance_history,
    delete_balance_history,
    delete_balances_history,
    get_balance_history_action_choices,
)

urlpatterns = [
    path('get/balances_history/', get_all_balance_history),
    path('delete/balance_history/<balance_history_id>/', delete_balance_history),
    path('delete/balances_history/', delete_balances_history),
    path('get/balance_history_action/', get_balance_history_action_choices),
]