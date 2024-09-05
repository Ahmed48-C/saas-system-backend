from django.contrib import admin

# Register your models here.
from app.features.balance.models import Balance

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'amount',
        'operator',
    ]
