from django.urls import path
from app.features.expense.views import (
    get_all_expense,
    create_expense,
    update_expense,
    delete_expense,
    get_expense_by_id,
    delete_expenses,
    get_all_expense_category,
    create_expense_category,
    get_last_30_days_expenses,
    get_current_month_expenses,
)

urlpatterns = [
    path('get/expense/<expense_id>/', get_expense_by_id),
    path('get/expenses/', get_all_expense),
    path('post/expense/', create_expense),
    path('put/expense/<expense_id>/', update_expense),
    path('delete/expense/<expense_id>/', delete_expense),
    path('delete/expenses/', delete_expenses),
    path('get/expense_categories/', get_all_expense_category),
    path('post/expense_category/', create_expense_category),
    path('get/expenses/last-30-days/', get_last_30_days_expenses),
    path('get/expenses/current-month/', get_current_month_expenses),
]
