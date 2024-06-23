from django.contrib import admin

# Register your models here.
from app.models import TestModel

@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):

    list_display = [
        'name',
    ]