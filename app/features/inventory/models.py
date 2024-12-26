from django.db import models
from app.features.inventory.querymanagers import InventoryQueryManager
from app.features.operator.models import Operator
from app.features.store.models import Store
from app.features.product.models import Product
# Create your models here.

class Inventory(models.Model):
    in_stock = models.IntegerField(max_length=80, blank=True, null=True)
    on_order = models.IntegerField(max_length=80, blank=True, null=True)
    reserved = models.IntegerField(max_length=80, blank=True, null=True)
    min_stock = models.IntegerField(max_length=80, blank=True, null=True)
    max_stock = models.IntegerField(max_length=80, blank=True, null=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = InventoryQueryManager()

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
        return str(self.in_stock)

    class Meta:
        unique_together = ('product', 'store')
        constraints = [
            models.UniqueConstraint(fields=['product', 'store'], name='unique_product_store')
        ]