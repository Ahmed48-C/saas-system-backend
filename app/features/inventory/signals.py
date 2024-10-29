# app/features/inventory/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from app.features.inventory.models import Inventory
from app.features.store.models import Store
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Cast

# Signal to update total_stock when an inventory is added/updated
@receiver([post_save, post_delete], sender=Inventory)
def update_total_stock(sender, instance, **kwargs):
    store = instance.store  # Get the store related to the inventory
    # Cast 'in_stock' to integer before summing
    total_stock = Inventory.objects.filter(store=store).aggregate(
        total=Sum(Cast('in_stock', models.IntegerField()))
    )['total'] or 0
    store.total_stock = total_stock
    store.save()
