from django.db import models
from django.utils import timezone
from app.features.store.models import Store
from app.features.product.models import Product
from app.features.userprofile.models import UserProfile
from app.features.inventory_log.querymanagers import InventoryLogQueryManager
# Create your models here.

class ActionLog(models.TextChoices):
    ADD = 'ADD', 'Add'
    MINUS = 'MINUS', 'Minus'
    NEW_PRODUCT = 'NEW_PRODUCT', 'New Product'

class AutoNoteLog(models.TextChoices):
    NEW_PURCHASE_ORDER = 'NEW_PURCHASE_ORDER', 'New Purchase Order' # add stock, because new purchase order created
    UPDATE_PURCHASE_ORDER = 'UPDATE_PURCHASE_ORDER', 'Update Purchase Order' # add/minus stock, because purchase order is updated
    REVERT_PURCHASE_ORDER = 'REVERT_PURCHASE_ORDER', 'Revert Purchase Order' # add back stock, because purchase order is changed from completed to pending status
    DELETE_PURCHASE_ORDER = 'DELETE_PURCHASE_ORDER', 'Delete Purchase Order' # minus stock, because purchase order with completed status is deleted
    COMPLETED_SALES_ORDER = 'COMPLETED_SALES_ORDER', 'New Sales Order' # minus stock, because new sales order created
    
    INCREASE_UPDATE_STOCK = 'INCREASE_UPDATE_STOCK', 'Increase Update Stock' # manual update stock with adding more stock
    DECREASE_UPDATE_STOCK = 'DECREASE_UPDATE_STOCK', 'Decrease Update Stock' # manual update stock with minus less stock
    NEW_PRODUCT = 'NEW_PRODUCT', 'New Product' # new product added to store

class InventoryLog(models.Model):

    userprofile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    action = models.CharField(max_length=100, choices=ActionLog.choices)
    action_date = models.DateTimeField(null=True, blank=True, default=timezone.now)
    auto_generated_note = models.CharField(max_length=400, choices=AutoNoteLog.choices)

    stock = models.IntegerField(max_length=80, blank=True, null=True)
    stock_before_action = models.IntegerField(max_length=80, blank=True, null=True)
    stock_after_action = models.IntegerField(max_length=80, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = InventoryLogQueryManager()

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
        return str(self.action) + " - " + str(self.action_date)