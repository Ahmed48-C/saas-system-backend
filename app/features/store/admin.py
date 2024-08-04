from django.contrib import admin

# Register your models here.
from app.features.store.models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):

    list_display = [
        'code',
        'name',
        'note',
        'street',
        'city',
        'state',
        'postcode',
        'country',
    ]
