from django.db import models
from app.features.sales_order.querymanagers import SalesOrderQueryManager
from app.features.operator.models import Operator
from app.features.store.models import Store
from app.features.product.models import Product
from app.features.balance.models import Balance
from app.features.customer.models import Customer
# Create your models here.

class SalesStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    COMPLETED = 'Completed', 'Completed'
    DELIVERY = 'Delivery', 'Delivery'


class SalesOrder(models.Model):
    code = models.CharField(max_length=80)
    total = models.DecimalField(max_digits=35, decimal_places=2)
    status = models.CharField(max_length=50, choices=SalesStatus.choices, default=SalesStatus.PENDING)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    balance = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)

    objects = SalesOrderQueryManager()

    def __str__(self):
        return f"SalesOrder - ID:{self.id},Code:{self.code}"

class SalesItem(models.Model):
    price = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=35, decimal_places=2)
    quantity = models.IntegerField()

    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f"SalesItem - ID:{self.id},Product:{self.product.name}"