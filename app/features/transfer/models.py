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

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = TransferQueryManager()

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
        return self.amount