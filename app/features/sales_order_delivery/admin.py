from django.contrib import admin

# Register your models here.
from app.features.sales_order_delivery.models import SalesOrderDelivery



@admin.register(SalesOrderDelivery)
class SalesOrderDeliveryAdmin(admin.ModelAdmin):

    list_display = [
        'sales_order',
        'pickup_at',
        'delivery_at',
        'courier',
        'tracking_number',
        'delivery_cost',
        'is_free_delivery',
        'notes',
    ]
