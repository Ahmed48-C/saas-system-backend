from django.contrib import admin

# Register your models here.
from app.features.transfer.models import Transfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):

    list_display = [
        'amount',
        'note',
        'date',
        'operator',
        'balance_from',
        'balance_to',
    ]
