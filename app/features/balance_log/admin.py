from django.contrib import admin

# Register your models here.
from app.features.balance_log.models import BalanceLog


@admin.register(BalanceLog)
class BalanceLogAdmin(admin.ModelAdmin):

    list_display = [
        'amount',
        'type',
        'note',
        'date',
        'action',
        'operator',
        'balance',
    ]
