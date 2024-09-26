from django.db import models
from app.features.transfer.querymanagers import TransferQueryManager
from app.features.operator.models import Operator
from app.features.balance.models import Balance
# Create your models here.

class Transfer(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    balance_from = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True, related_name='transfers_out')
    balance_to = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True, related_name='transfers_in')

    objects = TransferQueryManager()

    def __str__(self):
        return self.amount