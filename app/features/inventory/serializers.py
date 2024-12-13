from django.utils import timezone
from rest_framework import serializers
from app.features.inventory.models import Inventory
from app.features.inventory_log.models import ActionLog, AutoNoteLog
from app.features.inventory_log.services import InventoryLogService



class GetSingleInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = [
            'id',
            'in_stock',
            'on_order',
            'reserved',
            'min_stock',
            'max_stock',
            'operator_id',
            'store_id',
            'product_id',
        ]


class InventoryGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    store = serializers.SerializerMethodField('get_store_name')
    product = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = Inventory
        fields = [
            'id',
            'in_stock',
            'on_order',
            'reserved',
            'min_stock',
            'max_stock',
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


class InventoryCreateUpdateSerializer(serializers.ModelSerializer):
    # operator_id = serializers.CharField(max_length=10)
    store_id = serializers.CharField(max_length=10)
    product_id = serializers.CharField(max_length=10)

    def validate(self, attrs):
        # Convert empty strings to None
        for field in ['in_stock', 'on_order', 'reserved', 'min_stock', 'max_stock']:
            if attrs.get(field) == '':
                attrs[field] = None
        return attrs

    class Meta:
        model = Inventory
        fields = [
            'in_stock',
            'on_order',
            'reserved',
            'min_stock',
            'max_stock',
            # 'operator_id',
            'store_id',
            'product_id',
        ]

    def create(self, validated_data):
        Inventory.objects.create(**validated_data)
        # super().create(validated_data)
        # new_stock = int(validated_data['in_stock'])
        new_stock = int(validated_data.get('in_stock') or 0)
        InventoryLogService().add_inventory_log(
            userprofile_id = None, #TODO
            product_id = validated_data['product_id'],
            store_id = validated_data['store_id'],
            stock = 0,
            action = ActionLog.NEW_PRODUCT,
            auto_generated_note = AutoNoteLog.NEW_PRODUCT,
            stock_before_action = 0,
            stock_after_action = new_stock,
        )
        return validated_data
    
    def update(self, instance, validated_data):
        # Handle null or missing values for `in_stock`
        current_stock = int(instance.in_stock or 0)
        new_stock = int(validated_data.get('in_stock') or 0)
        
        # Skip adding an inventory log if both stocks are 0
        if current_stock == 0 and new_stock == 0:
            return super().update(instance, validated_data)

        auto_note = shall_add_log = action = None

        if current_stock > new_stock:
            shall_add_log = True
            auto_note = AutoNoteLog.DECREASE_UPDATE_STOCK
            action = ActionLog.MINUS
        elif current_stock < new_stock:
            shall_add_log = True
            auto_note = AutoNoteLog.INCREASE_UPDATE_STOCK
            action = ActionLog.ADD

        if shall_add_log:
            InventoryLogService().add_inventory_log(
                userprofile_id=None,  # TODO
                product_id=instance.product.id,
                store_id=instance.store.id,
                stock=current_stock,
                action=action,
                auto_generated_note=auto_note,
                stock_before_action=current_stock,
                stock_after_action=new_stock,
            )

        super().update(instance, validated_data)
        return instance

    # def update(self, instance, validated_data):
    #     current_stock = instance.in_stock
    #     new_stock = int(validated_data['in_stock'])
    #     auto_note = shall_add_log = action = None

    #     if current_stock > new_stock:
    #         shall_add_log = True
    #         auto_note = AutoNoteLog.DECREASE_UPDATE_STOCK
    #         action = ActionLog.MINUS
    #     elif current_stock < new_stock:
    #         shall_add_log = True
    #         auto_note = AutoNoteLog.INCREASE_UPDATE_STOCK
    #         action = ActionLog.ADD

    #     InventoryLogService().add_inventory_log(
    #         userprofile_id = None, #TODO
    #         product_id = instance.product.id,
    #         store_id = instance.store.id,
    #         stock = current_stock,
    #         action = action,
    #         auto_generated_note = auto_note,
    #         stock_before_action = current_stock,
    #         stock_after_action = new_stock,
    #     )
    #     super().update(instance, validated_data)
    #     return instance