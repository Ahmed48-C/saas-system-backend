from django.contrib import admin

# Register your models here.
from app.features.inventory.models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    list_display = [
        'code',
        'in_stock',
        'on_order',
        'reserved',
        'min_stock',
        'max_stock',
        'operator',
        'store',
        'product',
    ]
