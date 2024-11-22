from django.contrib import admin

# Register your models here.
from app.features.sales_order.models import SalesOrder, SalesItem


class SalesItemAdminInline(admin.TabularInline):
    model = SalesItem

    fields = (
        'id',
        'price',
        'total',
        'quantity',
        'product',
    )

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):

    inlines = (SalesItemAdminInline,)

    list_display = [
        'code',
        'total',
        'status',
        'operator',
        'store',
        'balance',
        'customer',
        'client',
    ]
