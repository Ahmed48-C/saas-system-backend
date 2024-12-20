from django.db import models
from app.features.income.querymanagers import IncomeQueryManager
from app.features.operator.models import Operator
from app.features.balance.models import Balance
from app.features.customer.models import Customer
# Create your models here.

class IncomeCategory(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

class Income(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=80)
    note = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=80)
    currency = models.CharField(max_length=3)
    attachment = models.CharField(max_length=300, null=True, blank=True)
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, null=True, blank=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    balance = models.ForeignKey(Balance, on_delete=models.PROTECT, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True)

    objects = IncomeQueryManager()

    def __str__(self):
        return self.amount