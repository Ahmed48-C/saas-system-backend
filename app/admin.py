from django.contrib import admin

# Register your models here.
from app.models import TestModel, Location

@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):

    list_display = [
        'name',
    ]



@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

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
