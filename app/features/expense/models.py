from django.db import models
from app.features.expense.querymanagers import ExpenseQueryManager
from app.features.operator.models import Operator
from app.features.balance.models import Balance
from app.features.supplier.models import Supplier
# Create your models here.

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

class Expense(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=80)
    note = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=80)
    attachment = models.CharField(max_length=300, null=True, blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, null=True, blank=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    balance = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ExpenseQueryManager()

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