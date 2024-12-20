from django.contrib import admin

# Register your models here.
from app.features.income.models import Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):

    list_display = [
        'amount',
        'type',
        'note',
        'date',
        'action',
        'currency',
        'operator',
        'balance',
        'customer',
    ]
