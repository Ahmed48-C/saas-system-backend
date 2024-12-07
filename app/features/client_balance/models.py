from django.db import models
from app.features.client_balance.querymanagers import ClientBalanceQueryManager
from app.features.operator.models import Operator
from app.features.client.models import Client
# Create your models here.

class ClientBalance(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated_at = models.DateTimeField(max_length=80)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    objects = ClientBalanceQueryManager()

    def __str__(self):
        return self.name