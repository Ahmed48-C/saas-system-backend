from django.db import models
from app.features.supplier.querymanagers import SupplierQueryManager
from app.features.operator.models import Operator
from app.features.location.models import Location
# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    contact_name = models.CharField(max_length=80, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SupplierQueryManager()

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