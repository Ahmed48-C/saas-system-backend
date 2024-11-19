from django.db import models
from app.features.client.querymanagers import ClientQueryManager


class Client(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    share_percentage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    objects = ClientQueryManager()

    def __str__(self):
        return self.name