from django.utils import timezone
from rest_framework import serializers
from app.features.purchase_order.models import PurchaseOrder



class GetSinglePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'name',
            'price',
            'quantity',
            'total',
            'status',
            'operator_id',
            'store_id',
            'product_id',
        ]


class PurchaseOrderGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    store = serializers.SerializerMethodField('get_store_name')
    product = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'name',
            'price',
            'quantity',
            'total',
            'status',
            'operator',
            'store',
            'product',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_store_name(obj):
        return obj.store and obj.store.name

    @staticmethod
    def get_product_name(obj):
        return obj.product and obj.product.name


class PurchaseOrderCreateUpdateSerializer(serializers.ModelSerializer):
    # operator_id = serializers.CharField(max_length=10)
    store_id = serializers.CharField(max_length=10)
    product_id = serializers.CharField(max_length=10)

    class Meta:
        model = PurchaseOrder
        fields = [
            'name',
            'price',
            'quantity',
            'total',
            'status',
            # 'operator_id',
            'store_id',
            'product_id',
        ]