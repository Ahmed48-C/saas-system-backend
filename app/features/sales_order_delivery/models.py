from django.db import models
from app.features.sales_order.models import SalesOrder
from app.features.courier.models import Courier

# class DeliveryStatus(models.TextChoices):
#     PENDING = 'Pending', 'Pending'
#     DISPATCHED = 'Dispatched', 'Dispatched'
#     COMPLETED = 'Completed', 'Completed'


class SalesOrderDelivery(models.Model):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.PROTECT, related_name='delivery')
    pickup_at = models.DateTimeField(null=True, blank=True)
    delivery_at = models.DateTimeField(null=True, blank=True)
    # status = models.CharField(max_length=20, choices=DeliveryStatus, default=DeliveryStatus.PENDING)
    courier = models.ForeignKey(Courier, on_delete=models.PROTECT)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    delivery_cost = models.IntegerField(default=0)
    is_free_delivery = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    # def __str__(self):
    #     return f"SalesOrder - ID:{self.id},Code:{self.code}"

