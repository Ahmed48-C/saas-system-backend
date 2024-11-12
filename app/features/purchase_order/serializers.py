from django.utils import timezone
from rest_framework import serializers
from app.features.purchase_order.models import PurchaseOrder, PurchaseItem
from app.features.inventory.models import Inventory
from app.features.balance.models import Balance


# class GetSinglePurchaseOrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PurchaseOrder
#         fields = [
#             'id',
#             'code',
#             'price',
#             'quantity',
#             'total',
#             'status',
#             'operator_id',
#             'store_id',
#             'product_id',
#             'balance_id',
#         ]
class PurchaseItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField('get_product_name')

    class Meta:
        model = PurchaseItem
        fields = [
            'price',
            'quantity',
            'total',
            'product',
        ]

    @staticmethod
    def get_product_name(obj):
        return obj.product and obj.product.name


class PurchaseItemGetSingleSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(source='product.id', read_only=True)

    class Meta:
        model = PurchaseItem
        fields = [
            'price',
            'quantity',
            'total',
            'product_id',  # Include product ID
        ]

    @staticmethod
    def get_product_name(obj):
        return obj.product_id.name if obj.product_id else None


class GetSinglePurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseItemGetSingleSerializer(many=True)  # Include the nested items serializer

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'code',
            'total',
            'status',
            'operator_id',
            'store_id',
            'balance_id',
            'supplier_id',
            'items',  # Add the nested items field here
        ]

# class PurchaseOrderGetAllSerializer(serializers.ModelSerializer):
#     operator = serializers.SerializerMethodField('get_operator_name')
#     store = serializers.SerializerMethodField('get_store_name')
#     product = serializers.SerializerMethodField('get_product_name')
#     balance = serializers.SerializerMethodField('get_balance_name')

#     class Meta:
#         model = PurchaseOrder
#         fields = [
#             'id',
#             'code',
#             'price',
#             'quantity',
#             'total',
#             'status',
#             'operator',
#             'store',
#             'product',
#             'balance',
#         ]

#     @staticmethod
#     def get_operator_name(obj):
#         return obj.operator and obj.operator.name

#     @staticmethod
#     def get_store_name(obj):
#         return obj.store and obj.store.name

#     @staticmethod
#     def get_product_name(obj):
#         return obj.product and obj.product.name

#     @staticmethod
#     def get_balance_name(obj):
#         return obj.balance and obj.balance.name


class PurchaseOrderGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    store = serializers.SerializerMethodField('get_store_name')
    balance = serializers.SerializerMethodField('get_balance_name')
    supplier = serializers.SerializerMethodField('get_supplier_name')
    items = PurchaseItemSerializer(many=True)  # Include the nested items serializer

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'code',
            'total',
            'status',
            'operator',
            'store',
            'balance',
            'supplier',
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
    def get_supplier_name(obj):
        return obj.supplier and obj.supplier.name

# class PurchaseOrderCreateUpdateSerializer(serializers.ModelSerializer):
#     # operator_id = serializers.CharField(max_length=10)
#     store_id = serializers.CharField(max_length=10)
#     product_id = serializers.CharField(max_length=10)
#     balance_id = serializers.CharField(max_length=10)

#     class Meta:
#         model = PurchaseOrder
#         fields = [
#             'code',
#             'price',
#             'quantity',
#             'total',
#             'status',
#             # 'operator_id',
#             'store_id',
#             'product_id',
#             'balance_id',
#         ]


class PurchaseItemCreateUpdateSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(max_length=10)  # We'll accept product_id in the request

    class Meta:
        model = PurchaseItem
        fields = ['price', 'quantity', 'total', 'product_id']

class PurchaseOrderCreateUpdateSerializer(serializers.ModelSerializer):
    store_id = serializers.CharField(max_length=10)
    balance_id = serializers.CharField(max_length=10)
    supplier_id = serializers.CharField(max_length=10)
    items = PurchaseItemCreateUpdateSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'code',
            'total',
            'status',
            'store_id',
            'balance_id',
            'supplier_id',
            'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Extract purchase items data

        status_order = validated_data.get('status')
        total = validated_data.get('total')
        store_id = validated_data.get('store_id')
        balance_id = validated_data.get('balance_id')
        supplier_id = validated_data.get('supplier_id')

        # Fetch the balance associated with the balance_id
        try:
            balance = Balance.objects.get(id=balance_id)
        except Balance.DoesNotExist:
            raise serializers.ValidationError({"balance": "Balance not found."})

        # Check if the total minus the balance amount would go negative
        # if balance.amount - total < 0:
        #     raise serializers.ValidationError({
        #         "detail": "The total amount exceeds the available balance. Please adjust the order or add funds."
        #     })

        # If status is 'Completed', update inventory
        if status_order.upper() == "COMPLETED":
            if balance.amount - total < 0:
                raise serializers.ValidationError({
                    "detail": "The total amount exceeds the available balance. Please adjust the order or add funds."
                })

            for item_data in items_data:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity')

                try:
                    inventory = Inventory.objects.get(
                        product=product_id,
                        store=store_id,
                        supplier=supplier_id,
                    )

                    # Convert inventory.in_stock to integer if it's a string
                    inventory_in_stock = int(inventory.in_stock) if inventory.in_stock else 0
                    new_in_stock = inventory_in_stock + quantity

                    # Check if new_in_stock exceeds max_stock, if max_stock is set
                    if inventory.max_stock:
                        max_stock = int(inventory.max_stock)
                        if new_in_stock > max_stock:
                            raise serializers.ValidationError({
                                "detail": f"Cannot add {quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
                            })

                    # # Deduct the total from the balance
                    # balance.amount -= total
                    # balance.save()


                    # Save new_in_stock back as string
                    inventory.in_stock = str(new_in_stock)
                    inventory.save()

                except Inventory.DoesNotExist:
                    # Create new inventory if it does not exist
                    Inventory.objects.create(
                        in_stock=str(quantity),  # Save as string
                        product_id=product_id,
                        store_id=store_id,
                        supplier_id=supplier_id,
                        # code=validated_data.get('code')
                    )

        # Deduct the total from the balance
            balance.amount -= total
            balance.save()

        # Create the PurchaseOrder after inventory and balance updates
        purchase_order = PurchaseOrder.objects.create(
            code=validated_data['code'],
            total=total,
            status=status_order,
            store_id=store_id,
            balance_id=balance_id,
            supplier_id=supplier_id
        )

        # Create the PurchaseItem(s) for this PurchaseOrder
        for item_data in items_data:
            PurchaseItem.objects.create(
                price=item_data['price'],
                quantity=item_data['quantity'],
                total=item_data['total'],
                product_id=item_data['product_id'],
                purchase_order=purchase_order
            )

        return purchase_order

    # def update(self, instance, validated_data):
    #     items_data = validated_data.pop('items')
    #     updated_status = validated_data.get('status')
    #     updated_total = validated_data.get('total')
    #     updated_store_id = validated_data.get('store_id')
    #     balance_id = validated_data.get('balance_id')

    #     original_status = instance.status
    #     original_total = instance.total
    #     original_store = instance.store
    #     original_items = list(instance.items.all())  # Retrieve original items for inventory adjustment

    #     # Fetch the balance associated with the balance_id
    #     # try:
    #     #     balance = Balance.objects.get(id=balance_id)
    #     # except Balance.DoesNotExist:
    #     #     raise serializers.ValidationError({"balance": "Balance not found."})

    #     # # Calculate the balance adjustment (difference between original and updated totals)
    #     # balance_adjustment = updated_total - original_total

    #     # # Ensure the balance can cover the difference
    #     # if balance.amount - balance_adjustment < 0:
    #     #     raise serializers.ValidationError({
    #     #         "detail": "Insufficient balance to complete the update."
    #     #     })

    #     # Fetch the balance associated with the balance_id
    #     try:
    #         balance = Balance.objects.get(id=balance_id)
    #     except Balance.DoesNotExist:
    #         raise serializers.ValidationError({"balance": "Balance not found."})

    #     # Handle balance adjustment only if status is 'Completed'
    #     if updated_status == 'Completed':
    #         balance_adjustment = updated_total - original_total
    #         # Ensure the balance can cover the difference
    #         if balance.amount - balance_adjustment < 0:
    #             raise serializers.ValidationError({
    #                 "detail": "Insufficient balance to complete the update."
    #             })
    #         # Deduct/add the difference to/from the balance
    #         balance.amount -= balance_adjustment
    #         balance.save()

    #     # If changing from 'Completed' to 'Pending', refund the balance
    #     if original_status == 'Completed' and updated_status == 'Pending':
    #         balance.amount += original_total
    #         balance.save()

    #     # Update inventory based on status changes
    #     if original_status == 'Pending' and updated_status == 'Completed':
    #         self._update_inventory_on_completion(items_data, updated_store_id, validated_data.get('code'))
    #     elif original_status == 'Completed' and updated_status == 'Pending':
    #         self._revert_inventory_on_pending(original_items, original_store)
    #     elif original_status == 'Completed' and updated_status == 'Completed':
    #         self._adjust_inventory_on_update(original_items, items_data, original_store, updated_store_id)

    #     # Deduct/add the difference to/from the balance
    #     # balance.amount -= balance_adjustment
    #     # balance.save()

    #     # Update the purchase order instance with the validated data
    #     instance.code = validated_data.get('code', instance.code)
    #     instance.total = updated_total
    #     instance.status = updated_status
    #     instance.store_id = updated_store_id
    #     instance.balance_id = balance_id
    #     instance.save()

    #     # Update the PurchaseItem(s) related to this PurchaseOrder
    #     self._update_purchase_items(instance, items_data)

    #     return instance

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        updated_status = validated_data.get('status')
        updated_total = validated_data.get('total')
        updated_store_id = validated_data.get('store_id')
        balance_id = validated_data.get('balance_id')
        supplier_id = validated_data.get('supplier_id')

        original_status = instance.status
        original_total = instance.total
        original_store = instance.store
        original_supplier = instance.supplier
        original_items = list(instance.items.all())  # Retrieve original items for inventory adjustment

        # Fetch the balance associated with the balance_id
        try:
            balance = Balance.objects.get(id=balance_id)
        except Balance.DoesNotExist:
            raise serializers.ValidationError({"balance": "Balance not found."})

        # Balance adjustment based on status change
        if original_status.upper() == 'PENDING' and updated_status.upper() == 'COMPLETED':
            # Deduct the updated total from the balance
            balance_adjustment = updated_total
            if balance.amount - balance_adjustment < 0:
                raise serializers.ValidationError({
                    "detail": "Insufficient balance to complete the update."
                })
            balance.amount -= balance_adjustment
            balance.save()

        # If changing from 'COMPLETED' to 'Pending', refund the balance
        if original_status.upper() == 'COMPLETED' and updated_status.upper() == 'PENDING':
            balance.amount += original_total
            balance.save()

        # If staying in Completed and total has changed, adjust balance accordingly
        if original_status.upper() == 'COMPLETED' and updated_status.upper() == 'COMPLETED' and original_total != updated_total:
            balance_adjustment = updated_total - original_total
            if balance.amount - balance_adjustment < 0:
                raise serializers.ValidationError({
                    "detail": "Insufficient balance to complete the update."
                })
            balance.amount -= balance_adjustment
            balance.save()

        # Update inventory based on status changes
        if original_status.upper() == 'PENDING' and updated_status.upper() == 'COMPLETED':
            # self._update_inventory_on_completion(items_data, updated_store_id, validated_data.get('code'))
            self._update_inventory_on_completion(items_data, updated_store_id, supplier_id)
        elif original_status.upper() == 'COMPLETED' and updated_status.upper() == 'PENDING':
            self._revert_inventory_on_pending(original_items, original_store, original_supplier)
        elif original_status.upper() == 'COMPLETED' and updated_status.upper() == 'COMPLETED':
            self._adjust_inventory_on_update(original_items, items_data, original_store, updated_store_id, original_supplier, supplier_id)

        # Update the purchase order instance with the validated data
        # instance.code = validated_data.get('code', instance.code)
        instance.total = updated_total
        instance.status = updated_status
        instance.store_id = updated_store_id
        instance.balance_id = balance_id
        instance.supplier_id = supplier_id
        instance.save()

        # Update the PurchaseItem(s) related to this PurchaseOrder
        self._update_purchase_items(instance, items_data)

        return instance


    def _update_inventory_on_completion(self, items_data, store_id, supplier_id):
        for item_data in items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')

            try:
                inventory = Inventory.objects.get(product=product_id, store=store_id, supplier=supplier_id)
                inventory_in_stock = int(inventory.in_stock) if inventory.in_stock else 0
                new_in_stock = inventory_in_stock + quantity

                if inventory.max_stock:
                    max_stock = int(inventory.max_stock)
                    if new_in_stock > max_stock:
                        raise serializers.ValidationError({
                            "detail": f"Cannot add {quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
                        })

                inventory.in_stock = new_in_stock
                inventory.save()

            except Inventory.DoesNotExist:
                Inventory.objects.create(
                    in_stock=str(quantity),
                    product_id=product_id,
                    store_id=store_id,
                    supplier_id=supplier_id,
                    # code=code
                )

    def _revert_inventory_on_pending(self, original_items, store, supplier):
        for item in original_items:
            try:
                inventory = Inventory.objects.get(product=item.product, store=store, supplier=supplier)
                inventory_in_stock = int(inventory.in_stock) if inventory.in_stock else 0
                new_in_stock = inventory_in_stock - item.quantity

                inventory.in_stock = str(new_in_stock)
                inventory.save()

            except Inventory.DoesNotExist:
                pass

    # def _adjust_inventory_on_update(self, original_items, updated_items_data, original_store, updated_store_id, original_supplier, supplier_id):
    #     if original_store.id != updated_store_id:
    #         self._revert_inventory_on_pending(original_items, original_store)
    #         # self._update_inventory_on_completion(updated_items_data, updated_store_id, code=None)
    #         self._update_inventory_on_completion(updated_items_data, updated_store_id)
    #     else:
    #         for original_item, updated_item_data in zip(original_items, updated_items_data):
    #             product_id = updated_item_data.get('product_id')
    #             updated_quantity = updated_item_data.get('quantity')

    #             try:
    #                 inventory = Inventory.objects.get(product=product_id, store=original_store)
    #                 inventory_in_stock = int(inventory.in_stock) if inventory.in_stock else 0
    #                 new_in_stock = inventory_in_stock + updated_quantity - original_item.quantity

    #                 if inventory.max_stock:
    #                     max_stock = int(inventory.max_stock)
    #                     if new_in_stock > max_stock:
    #                         raise serializers.ValidationError({
    #                             "detail": f"Cannot adjust inventory by {updated_quantity - original_item.quantity}. "
    #                                     f"Maximum stock level of {max_stock} would be exceeded."
    #                         })

    #                 inventory.in_stock = str(new_in_stock)
    #                 inventory.save()

    #             except Inventory.DoesNotExist:
    #                 pass
    
    def _adjust_inventory_on_update(self, original_items, updated_items_data, original_store, updated_store_id, original_supplier, updated_supplier_id):
        # Check if the store has changed
        if original_store.id != updated_store_id:
            # Revert inventory changes for the original store
            self._revert_inventory_on_pending(original_items, original_store, original_supplier)
            # Update inventory for the new store
            self._update_inventory_on_completion(updated_items_data, updated_store_id, updated_supplier_id)
        
        # Check if the supplier has changed
        if original_supplier.id != updated_supplier_id:
            # Revert inventory changes for the original supplier
            self._revert_inventory_on_pending(original_items, original_store, original_supplier)
            # Update inventory for the new supplier
            self._update_inventory_on_completion(updated_items_data, updated_store_id, updated_supplier_id)
        
        # If neither store nor supplier has changed, simply update the inventory quantities
        if original_store.id == updated_store_id and original_supplier.id == updated_supplier_id:
            for original_item, updated_item_data in zip(original_items, updated_items_data):
                try:
                    inventory = Inventory.objects.get(
                        product=original_item.product,
                        store=original_store,
                        supplier=original_supplier
                    )

                    # Calculate the difference in quantity
                    original_quantity = original_item.quantity
                    updated_quantity = updated_item_data.get('quantity')
                    quantity_difference = updated_quantity - original_quantity

                    inventory_in_stock = int(inventory.in_stock) if inventory.in_stock else 0
                    new_in_stock = inventory_in_stock + quantity_difference

                    # Ensure new stock doesn't exceed max stock
                    if inventory.max_stock:
                        max_stock = int(inventory.max_stock)
                        if new_in_stock > max_stock:
                            raise serializers.ValidationError({
                                "detail": f"Cannot add {quantity_difference} to inventory. Maximum stock level of {max_stock} would be exceeded."
                            })

                    inventory.in_stock = str(new_in_stock)
                    inventory.save()

                except Inventory.DoesNotExist:
                    pass

    def _update_purchase_items(self, purchase_order, items_data):
        # Clear existing items and recreate them
        PurchaseItem.objects.filter(purchase_order=purchase_order).delete()

        for item_data in items_data:
            PurchaseItem.objects.create(
                price=item_data['price'],
                quantity=item_data['quantity'],
                total=item_data['total'],
                product_id=item_data['product_id'],
                purchase_order=purchase_order
            )
