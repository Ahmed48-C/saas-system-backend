from django.contrib import admin

# Register your models here.
from app.features.expense.models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    list_display = [
        'amount',
        'type',
        'note',
        'date',
        'action',
        'operator',
        'balance',
        'supplier',
    ]
