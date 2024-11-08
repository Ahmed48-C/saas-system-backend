from django.utils import timezone
from rest_framework import serializers
from app.features.sales_order.models import SalesOrder, SalesItem
from app.features.inventory.models import Inventory
from app.features.balance.models import Balance



class SalesItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = SalesItem
        fields = [
            'price',
            'quantity',
            'total',
            'product',
        ]

    @staticmethod
    def get_product_name(obj):
        return obj.product and obj.product.name


class SalesItemGetSingleSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(source='product.id', read_only=True)

    class Meta:
        model = SalesItem
        fields = [
            'price',
            'quantity',
            'total',
            'product_id',  # Include product ID
        ]

    @staticmethod
    def get_product_name(obj):
        return obj.product_id.name if obj.product_id else None


class GetSingleSalesOrderSerializer(serializers.ModelSerializer):
    items = SalesItemGetSingleSerializer(many=True)  # Include the nested items serializer

    class Meta:
        model = SalesOrder
        fields = [
            'id',
            'code',
            'total',
            'status',
            'operator_id',
            'store_id',
            'balance_id',
            'customer_id',
            'items',  # Add the nested items field here
        ]


class SalesOrderGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    store = serializers.SerializerMethodField('get_store_name')
    balance = serializers.SerializerMethodField('get_balance_name')
    customer = serializers.SerializerMethodField('get_customer_name')
    items = SalesItemSerializer(many=True)  # Include the nested items serializer

    class Meta:
        model = SalesOrder
        fields = [
            'id',
            'code',
            'total',
            'status',
            'operator',
            'store',
            'balance',
            'customer',
            'items',    # Add the nested items field
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_store_name(obj):
        return obj.store and obj.store.name

    @staticmethod
    def get_balance_name(obj):
        return obj.balance and obj.balance.name

    @staticmethod
    def get_customer_name(obj):
        return obj.customer and obj.customer.name


class SalesItemCreateUpdateSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(max_length=10)  # We'll accept product_id in the request

    class Meta:
        model = SalesItem
        fields = ['price', 'quantity', 'total', 'product_id']

class SalesOrderCreateUpdateSerializer(serializers.ModelSerializer):
    store_id = serializers.CharField(max_length=10)
    balance_id = serializers.CharField(max_length=10)
    customer_id = serializers.CharField(max_length=10)
    items = SalesItemCreateUpdateSerializer(many=True)

    class Meta:
        model = SalesOrder
        fields = [
            'code',
            'total',
            'status',
            'store_id',
            'balance_id',
            'customer_id',
            'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Extract sales items data

        status_order = validated_data.get('status')
        total = validated_data.get('total')
        store_id = validated_data.get('store_id')
        balance_id = validated_data.get('balance_id')
        customer_id = validated_data.get('customer_id')

        # Fetch the balance associated with the balance_id
        try:
            balance = Balance.objects.get(id=balance_id)
        except Balance.DoesNotExist:
            raise serializers.ValidationError({"balance": "Balance not found."})

        # Create the SalesOrder after inventory and balance updates
        sales_order = SalesOrder.objects.create(
            code=validated_data['code'],
            total=total,
            status=status_order,
            store_id=store_id,
            balance_id=balance_id,
            customer_id=customer_id
        )

        # Create the SalesItem(s) for this SalesOrder
        for item_data in items_data:
            SalesItem.objects.create(
                price=item_data['price'],
                quantity=item_data['quantity'],
                total=item_data['total'],
                product_id=item_data['product_id'],
                sales_order=sales_order
            )

        return sales_order


    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        updated_status = validated_data.get('status')
        updated_total = validated_data.get('total')
        updated_store_id = validated_data.get('store_id')
        balance_id = validated_data.get('balance_id')
        customer_id = validated_data.get('customer_id')

        original_status = instance.status
        original_total = instance.total
        original_store = instance.store
        original_customer = instance.customer
        original_items = list(instance.items.all())  # Retrieve original items for inventory adjustment

        # Fetch the balance associated with the balance_id
        try:
            balance = Balance.objects.get(id=balance_id)
        except Balance.DoesNotExist:
            raise serializers.ValidationError({"balance": "Balance not found."})


        instance.total = updated_total
        instance.status = updated_status
        instance.store_id = updated_store_id
        instance.balance_id = balance_id
        instance.customer_id = customer_id
        instance.save()

        return instance