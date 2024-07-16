from django.db import models
from app.features.supplier.querymanagers import SupplierQueryManager
from app.features.operator.models import Operator
from app.features.location.models import Location
# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=80, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    contact_name = models.CharField(max_length=80, null=True, blank=True)
    contact_phone = models.CharField(max_length=80, null=True, blank=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)

    objects = SupplierQueryManager()

    def __str__(self):
        return self.name