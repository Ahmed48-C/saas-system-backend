from django.db import models
from app.features.purchase_order.querymanagers import PurchaseOrderQueryManager
from app.features.operator.models import Operator
from app.features.store.models import Store
from app.features.product.models import Product
from app.features.balance.models import Balance
from app.features.supplier.models import Supplier
# Create your models here.

class PurchaseOrder(models.Model):
    code = models.CharField(max_length=80)
    total = models.DecimalField(max_digits=35, decimal_places=2)
    status = models.CharField(max_length=50)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    balance = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, blank=True)

    objects = PurchaseOrderQueryManager()

    def __str__(self):
        return self.code

class PurchaseItem(models.Model):
    price = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=35, decimal_places=2)
    quantity = models.IntegerField()

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product.name}"