from django.contrib import admin

# Register your models here.
from app.features.customer.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = [
        'code',
        'name',
        'phone',
        'email',
        'operator',
        'location',
    ]
