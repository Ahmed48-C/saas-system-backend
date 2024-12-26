from django.urls import path
from app.features.income.views import (
    get_all_income,
    create_income,
    update_income,
    delete_income,
    get_income_by_id,
    delete_incomes,
    get_all_income_category,
    create_income_category,
    get_last_30_days_incomes,
    get_current_month_incomes,
)

urlpatterns = [
    path('get/income/<income_id>/', get_income_by_id),
    path('get/incomes/', get_all_income),
    path('post/income/', create_income),
    path('put/income/<income_id>/', update_income),
    path('delete/income/<income_id>/', delete_income),
    path('delete/incomes/', delete_incomes),
    path('get/income_categories/', get_all_income_category),
    path('post/income_category/', create_income_category),
    path('get/incomes/last-30-days/', get_last_30_days_incomes),
    path('get/incomes/current-month/', get_current_month_incomes),
]
