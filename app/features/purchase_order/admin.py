from django.contrib import admin

# Register your models here.
from app.features.purchase_order.models import PurchaseOrder, PurchaseItem


class PurchaseItemAdminInline(admin.TabularInline):
    model = PurchaseItem

    fields = (
        'id',
        'price',
        'total',
        'quantity',
        'product',
    )

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):

    inlines = (PurchaseItemAdminInline,)

    list_display = [
        'code',
        'total',
        'status',
        'operator',
        'store',
        'balance',
    ]
