from django.contrib import admin

# Register your models here.
from app.features.supplier.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'phone',
        'email',
        'operator',
        'location',
    ]
