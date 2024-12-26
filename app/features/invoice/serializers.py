from django.utils import timezone
from rest_framework import serializers
from app.features.invoice.models import Invoice, InvoiceItem
from app.features.balance.models import Balance
from main.settings import IMAGE_PATH_CLOUDINARY

class InvoiceItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = InvoiceItem
        fields = [
            'price',
            'quantity',
            'total',
            'product',
        ]

    @staticmethod
    def get_product_name(obj):
        return obj.product and obj.product.name


class InvoiceItemGetSingleSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(source='product.id', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'price',
            'quantity',
            'total',
            'product_id',  # Include product ID
        ]

    @staticmethod
    def get_product_name(obj):
        return obj.product_id.name if obj.product_id else None


class InvoiceItemCreateUpdateSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(max_length=10)  # We'll accept product_id in the request

    class Meta:
        model = InvoiceItem
        fields = ['price', 'quantity', 'total', 'product_id']


class GetSingleInvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemGetSingleSerializer(many=True)
    attachment_file = serializers.SerializerMethodField('get_attachment_file')

    class Meta:
        model = Invoice
        fields = [
            'id',
            'number',
            'date',
            'due_date',
            'payment_method',
            'total',
            'note',
            'attachment_file',
            'customer_id',
            'location_id',
            'operator_id',
            'items',
        ]
    
    @staticmethod
    def get_attachment_file(obj):
        if obj.attachment:
            return IMAGE_PATH_CLOUDINARY + obj.attachment


class InvoiceGetAllSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField('get_customer_name')
    location = serializers.SerializerMethodField('get_location_name')
    operator = serializers.SerializerMethodField('get_operator_name')
    attachment_file = serializers.SerializerMethodField('get_attachment_file')
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'number',
            'date',
            'due_date',
            'payment_method',
            'total',
            'note',
            'attachment_file',
            'customer',
            'location',
            'operator',
            'items',
        ]
    
    @staticmethod
    def get_customer_name(obj):
        return obj.customer and obj.customer.name

    @staticmethod
    def get_location_name(obj):
        return obj.location and obj.location.name

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name
    
    @staticmethod
    def get_attachment_file(obj):
        if obj.attachment:
            return IMAGE_PATH_CLOUDINARY + obj.attachment


class InvoiceCreateUpdateSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(max_length=10)
    location_id = serializers.CharField(max_length=10, allow_null=True, required=False)
    items = InvoiceItemCreateUpdateSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'number',
            'date',
            'due_date',
            'payment_method',
            'total',
            'note',
            'attachment',
            'customer_id',
            'location_id',
            'items',
        ]

    def create(self, validated_data):
        # Extract items data before creating invoice
        items_data = validated_data.pop('items')
        
        # Create the invoice
        invoice = Invoice.objects.create(**validated_data)
        
        # Create each invoice item
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
            
        return invoice

    def update(self, instance, validated_data):
        # Extract items data
        items_data = validated_data.pop('items')
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Delete existing items and create new ones
        instance.items.all().delete()
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=instance, **item_data)
            
        return instance