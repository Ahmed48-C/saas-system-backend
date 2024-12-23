from django.contrib import admin

# Register your models here.
from app.features.invoice.models import Invoice, InvoiceItem

class InvoiceItemAdminInline(admin.TabularInline):
    model = InvoiceItem

    fields = (
        'id',
        'price',
        'total',
        'quantity',
        'product',
    )

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    inlines = (InvoiceItemAdminInline,)

    list_display = [
        'number',
        'date',
        'due_date',
        'currency',
        'payment_method',
        'total',
        'note',
        'customer',
        'location',
        'operator',
    ]
