from django.db import models
from app.features.product.querymanagers import ProductQueryManager
from app.features.supplier.models import Supplier
# Create your models here.

class Product(models.Model):
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=300, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, blank=True)

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

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ProductQueryManager()

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return self.name