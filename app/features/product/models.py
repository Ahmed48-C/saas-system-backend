from django.db import models
from app.features.product.querymanagers import ProductQueryManager
# from app.features.supplier.models import Supplier
# Create your models here.

class Product(models.Model):
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)

    brand = models.CharField(max_length=180, null=True, blank=True)

    measure_unit = models.CharField(max_length=80, blank=True, null=True)
    weight = models.CharField(max_length=80, blank=True, null=True)
    length = models.CharField(max_length=80, blank=True, null=True)
    width = models.CharField(max_length=80, blank=True, null=True)
    height = models.CharField(max_length=80, blank=True, null=True)
    color = models.CharField(max_length=80, blank=True, null=True)
    size = models.CharField(max_length=80, blank=True, null=True)
    dimension_unit = models.CharField(max_length=20, blank=True, null=True)
    weight_unit = models.CharField(max_length=20, blank=True, null=True)

    objects = ProductQueryManager()

    def __str__(self):
        return self.name