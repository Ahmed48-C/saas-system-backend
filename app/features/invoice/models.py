from django.db import models
from app.features.invoice.querymanagers import InvoiceQueryManager
from app.features.operator.models import Operator
from app.features.product.models import Product
from app.features.customer.models import Customer
from app.features.location.models import Location
# Create your models here.

class InvoicePaymentMethod(models.TextChoices):
    CASH = 'Cash', 'Cash'
    CREDIT_CARD = 'Credit Card', 'Credit Card'
    DEBIT_CARD = 'Debit Card', 'Debit Card'
    TRANSFER = 'Transfer', 'Transfer'
    CHECK = 'Check', 'Check'
    BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'
    OTHER = 'Other', 'Other'

class Invoice(models.Model):

    number = models.CharField(max_length=80)
    date = models.DateField()
    due_date = models.DateField()
    payment_method = models.CharField(max_length=80, choices=InvoicePaymentMethod.choices, null=True, blank=True)
    total = models.DecimalField(max_digits=35, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    attachment = models.CharField(max_length=300, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = InvoiceQueryManager()

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

class InvoiceItem(models.Model):
    price = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=35, decimal_places=2)
    quantity = models.IntegerField()

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product.name}"