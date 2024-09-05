from django.db import models
from app.features.balance_log.querymanagers import BalanceLogQueryManager
from app.features.operator.models import Operator
from app.features.balance.models import Balance
# Create your models here.

class BalanceLog(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=80)
    note = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=80)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    balance = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True)

    objects = BalanceLogQueryManager()

    def __str__(self):
        return self.amount