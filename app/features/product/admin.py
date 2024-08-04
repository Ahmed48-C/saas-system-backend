from django.contrib import admin

# Register your models here.
from app.features.product.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = [
        'code',
        'name',
        'description',
        'supplier',
        'brand',
        'measure_unit',
        'weight',
        'length',
        'width',
        'height',
        'color',
        'size',
        'dimension_unit',
        'weight_unit',
    ]
