
from django.contrib import admin
from app.features.inventory_log.models import InventoryLog


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = (
        'userprofile',
        'store',
        'product',
        'action',
        'action_date',
        'auto_generated_note',
        'stock',
        'stock_before_action',
        'stock_after_action',
    )
    list_filter = ['userprofile', 'action',]
    search_fields = [ 'action', 'action_date',]