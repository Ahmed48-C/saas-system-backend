from django.contrib import admin

# Register your models here.
from app.features.operator.models import Operator


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):

    list_display = [
        'name',
    ]
