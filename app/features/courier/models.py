from django.db import models
from app.features.courier.querymanagers import CourierQueryManager


class VehicleTypes(models.TextChoices):
    BIKE = 'Bike', 'Bike'
    CAR = 'Car', 'Car'
    VAN = 'Van', 'Van'

class Courier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50, choices=VehicleTypes.choices)
    is_available = models.BooleanField(default=True)
    default_delivery_cost = models.IntegerField(default=0)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CourierQueryManager()

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