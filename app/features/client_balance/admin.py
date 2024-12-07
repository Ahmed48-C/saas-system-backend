from django.contrib import admin

# Register your models here.
from app.features.client_balance.models import ClientBalance


@admin.register(ClientBalance)
class ClientBalanceAdmin(admin.ModelAdmin):

    list_display = [
        'client',
        'amount',
        'last_updated_at',
        'operator',
    ]
