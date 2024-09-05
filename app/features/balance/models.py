from django.db import models
from app.features.balance.querymanagers import BalanceQueryManager
from app.features.operator.models import Operator
# Create your models here.

class Balance(models.Model):
    name = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    objects = BalanceQueryManager()

    def __str__(self):
        return self.name