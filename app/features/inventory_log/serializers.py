from django.utils import timezone
from rest_framework import serializers
from app.features.inventory_log.models import InventoryLog



class GetSingleInventoryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLog
        fields = [
            'id',
            'userprofile',
            'store_id',
            'product_id',
            'action',
            'action_date',
            'auto_generated_note',
            'stock',
            'stock_before_action',
            'stock_after_action',
        ]


class InventoryLogGetAllSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField('get_store_name')
    product = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = InventoryLog
        fields = [
            'id',
            'userprofile',
            'store',
            'product',
            'action',
            'action_date',
            'auto_generated_note',
            'stock',
            'stock_before_action',
            'stock_after_action',
        ]

    @staticmethod
    def get_store_name(obj):
        return obj.store and obj.store.name

    @staticmethod
    def get_product_name(obj):
        return obj.product and obj.product.name


class InventoryLogCreateUpdateSerializer(serializers.ModelSerializer):
    store_id = serializers.CharField(max_length=10)
    product_id = serializers.CharField(max_length=10)

    class Meta:
        model = InventoryLog
        fields = [
            'userprofile',
            'store_id',
            'product_id',
            'action',
            'action_date',
            'auto_generated_note',
            'stock',
            'stock_before_action',
            'stock_after_action',
        ]