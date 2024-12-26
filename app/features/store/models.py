from django.db import models
from app.features.store.querymanagers import StoreQueryManager
from app.features.operator.models import Operator
# Create your models here.

class Store(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=80)
    note = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postcode = models.CharField(max_length=50)
    country = models.CharField(max_length=30)
    total_stock = models.PositiveIntegerField(default=0)  # New field to store total stock

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = StoreQueryManager()

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