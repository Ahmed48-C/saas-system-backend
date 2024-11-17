from django.contrib import admin

# Register your models here.
from app.features.courier.models import Courier


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):

    list_display = [
        'name',
    ]
