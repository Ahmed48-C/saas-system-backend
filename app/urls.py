from django.urls import path
from app.views import records_list

urlpatterns = [
    path('get/records/', records_list),
]