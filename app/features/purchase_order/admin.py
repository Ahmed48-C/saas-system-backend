from django.contrib import admin

# Register your models here.
from app.features.purchase_order.models import PurchaseOrder


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'price',
        'quantity',
        'total',
        'status',
        'operator',
        'store',
        'product',
        'balance',
    ]
