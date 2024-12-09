from django.contrib import admin

# Register your models here.
from app.features.balance_history.models import BalanceHistory

@admin.register(BalanceHistory)
class BalanceHistoryAdmin(admin.ModelAdmin):

    list_display = [
        'amount',
        'previous_amount',
        'current_amount',
        'balance',
        'action',
        'transfer_date',
        'operator',
    ]
