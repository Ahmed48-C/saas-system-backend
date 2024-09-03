from django.db import models
from app.features.inventory.querymanagers import InventoryQueryManager
from app.features.operator.models import Operator
from app.features.store.models import Store
from app.features.product.models import Product
# Create your models here.

class Inventory(models.Model):
    code = models.CharField(max_length=50)
    in_stock = models.CharField(max_length=80, blank=True, null=True)
    on_order = models.CharField(max_length=80, blank=True, null=True)
    reserved = models.CharField(max_length=80, blank=True, null=True)
    min_stock = models.CharField(max_length=80, blank=True, null=True)
    max_stock = models.CharField(max_length=80, blank=True, null=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)

    objects = InventoryQueryManager()

    def __str__(self):
        return self.code

    class Meta:
        unique_together = ('product', 'store')
        constraints = [
            models.UniqueConstraint(fields=['product', 'store'], name='unique_product_store')
        ]