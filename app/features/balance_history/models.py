from django.db import models
from app.features.balance_history.querymanagers import BalanceHistoryQueryManager
from app.features.operator.models import Operator
from app.features.balance.models import Balance
from django.utils import timezone
# Create your models here.

class ActionType(models.TextChoices):
    DEPOSIT = 'DEPOSIT', 'Deposit'
    WITHDRAW = 'WITHDRAW', 'Withdraw'

class BalanceHistory(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    previous_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    balance = models.ForeignKey(Balance, on_delete=models.SET_NULL, null=True, blank=True)

    action = models.CharField(max_length=100, choices=ActionType.choices, null=True, blank=True)
    note = models.CharField(max_length=100, null=True, blank=True)
    transfer_date = models.DateTimeField(null=True, blank=True, default=timezone.now)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    objects = BalanceHistoryQueryManager()

    def __str__(self):
        return self.name