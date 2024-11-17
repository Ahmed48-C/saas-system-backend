from django.db import models
from app.features.courier.querymanagers import CourierQueryManager


class Courier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50, choices=[
        ('Bike', 'Bike'),
        ('Car', 'Car'),
        ('Van', 'Van'),
    ])
    is_available = models.BooleanField(default=True)
    default_delivery_cost = models.IntegerField(default=0)

    objects = CourierQueryManager()

    def __str__(self):
        return self.name