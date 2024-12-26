from django.db import models
from app.features.location.querymanagers import LocationQueryManager
from app.features.operator.models import Operator
# Create your models here.

class TestModel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Location(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=80)
    note = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postcode = models.CharField(max_length=50)
    country = models.CharField(max_length=30)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = LocationQueryManager()

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