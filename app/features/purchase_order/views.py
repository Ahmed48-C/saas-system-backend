from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from app.features.purchase_order.serializers import (
    PurchaseOrderGetAllSerializer,
    PurchaseOrderCreateUpdateSerializer,
    GetSinglePurchaseOrderSerializer,
)

# Create your views here.

from app.features.purchase_order.models import PurchaseOrder
from app.features.inventory.models import Inventory


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_purchase_order(request):
    records, actual_total_count = PurchaseOrder.objects.get_all_by_limit(request)
    serializer = PurchaseOrderGetAllSerializer(records, many=True)

    json_obj = PurchaseOrder.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


# @api_view(['POST'])
# def create_purchase_order(request):
#     serializer = PurchaseOrderCreateUpdateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     purchase_order = serializer.save()

#     # Check if the status is 'completed'
#     if purchase_order.status == 'Completed':
#         # Search for existing inventory with the same product and store
#         try:
#             inventory = Inventory.objects.get(product=purchase_order.product, store=purchase_order.store)
#             # Update inventory in_stock
#             inventory.in_stock += purchase_order.quantity
#             inventory.save()
#         except Inventory.DoesNotExist:
#             # Create a new inventory record if not found
#             Inventory.objects.create(
#                 in_stock=purchase_order.quantity,
#                 product=purchase_order.product,
#                 store=purchase_order.store,
#                 code=purchase_order.name
#             )

#     return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def create_purchase_order(request):
#     serializer = PurchaseOrderCreateUpdateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     purchase_order = serializer.save()

#     if purchase_order.status == 'Completed':
#         try:
#             inventory = Inventory.objects.get(
#                 product=purchase_order.product,
#                 store=purchase_order.store
#             )

#             # Convert inventory.in_stock to integer if it's a string
#             inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#             inventory_in_stock += purchase_order.quantity

#             # Save inventory_in_stock back as string
#             inventory.in_stock = str(inventory_in_stock)
#             inventory.save()

#         except Inventory.DoesNotExist:
#             Inventory.objects.create(
#                 in_stock=str(purchase_order.quantity),  # Save as string
#                 product=purchase_order.product,
#                 store=purchase_order.store,
#                 code=purchase_order.name
#             )

#     return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_purchase_order(request):
    serializer = PurchaseOrderCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    status_order = validated_data.get('status')
    quantity = validated_data.get('quantity')
    store_id = validated_data.get('store_id')
    product_id = validated_data.get('product_id')

    if status_order == 'Completed':
        try:
            inventory = Inventory.objects.get(
                product=product_id,
                store=store_id
            )

            # Convert inventory.in_stock to integer if it's a string
            inventory_in_stock = int(inventory.in_stock) if inventory.in_stock and inventory.in_stock.isdigit() else 0
            new_in_stock = inventory_in_stock + quantity

            # Debugging outputs
            print(f"Inventory In Stock: {inventory_in_stock}")
            print(f"New In Stock: {new_in_stock}")

            # Check if new_in_stock exceeds max_stock, if max_stock is set
            if inventory.max_stock and inventory.max_stock.isdigit():
                max_stock = int(inventory.max_stock)
                print(f"Max Stock: {max_stock}")
                if new_in_stock > max_stock:
                    return Response({
                        "detail": f"Cannot add {quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Save new_in_stock back as string
            inventory.in_stock = str(new_in_stock)
            inventory.save()

        except Inventory.DoesNotExist:
            try:
                Inventory.objects.create(
                    in_stock=str(quantity),  # Save as string
                    product_id=product_id,
                    store_id=store_id,
                    code=validated_data.get('name')
                )
            except Exception as e:
                # If creation fails, return a meaningful error message
                return Response({
                    "detail": f"Failed to create inventory: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save the purchase order only after the inventory check
    purchase_order = serializer.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(['PUT'])
# def update_purchase_order(request, purchase_order_id):
#     try:
#         purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
#     except PurchaseOrder.DoesNotExist:
#         return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

#     # Save the original status, quantity, product, and store before the update
#     original_status = purchase_order.status
#     original_quantity = purchase_order.quantity
#     original_product = purchase_order.product
#     original_store = purchase_order.store

#     serializer = PurchaseOrderCreateUpdateSerializer(purchase_order, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     updated_purchase_order = serializer.save()

#     # Handle status change from Pending to Completed
#     if original_status == 'Pending' and updated_purchase_order.status == 'Completed':
#         _update_inventory_on_completion(updated_purchase_order)

#     # Handle status change from Completed to Pending
#     elif original_status == 'Completed' and updated_purchase_order.status == 'Pending':
#         _revert_inventory_on_pending(original_product, original_store, original_quantity)

#     # Handle changes in quantity, product, or store while status is Completed
#     elif original_status == 'Completed' and updated_purchase_order.status == 'Completed':
#         if original_product != updated_purchase_order.product or original_store != updated_purchase_order.store:
#             # Revert the inventory for the original product/store
#             _revert_inventory_on_pending(original_product, original_store, original_quantity)
#             # Update the inventory for the new product/store
#             _update_inventory_on_completion(updated_purchase_order)
#         elif original_quantity != updated_purchase_order.quantity:
#             # Update the inventory for the same product/store with the new quantity
#             _adjust_inventory_quantity(updated_purchase_order, original_quantity)

#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['PUT'])
# def update_purchase_order(request, purchase_order_id):
#     try:
#         purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
#     except PurchaseOrder.DoesNotExist:
#         return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

#     original_status = purchase_order.status
#     original_quantity = purchase_order.quantity
#     original_product = purchase_order.product
#     original_store = purchase_order.store

#     serializer = PurchaseOrderCreateUpdateSerializer(purchase_order, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     updated_purchase_order = serializer.save()

#     try:
#         if original_status == 'Pending' and updated_purchase_order.status == 'Completed':
#             _update_inventory_on_completion(updated_purchase_order)

#         elif original_status == 'Completed' and updated_purchase_order.status == 'Pending':
#             _revert_inventory_on_pending(original_product, original_store, original_quantity)

#         elif original_status == 'Completed' and updated_purchase_order.status == 'Completed':
#             if original_product != updated_purchase_order.product or original_store != updated_purchase_order.store:
#                 _revert_inventory_on_pending(original_product, original_store, original_quantity)
#                 _update_inventory_on_completion(updated_purchase_order)
#             elif original_quantity != updated_purchase_order.quantity:
#                 _adjust_inventory_quantity(updated_purchase_order, original_quantity)

#     except ValueError as e:
#         return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     return Response(serializer.data, status=status.HTTP_200_OK)

from django.db import transaction

@api_view(['PUT'])
def update_purchase_order(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    original_status = purchase_order.status
    original_quantity = purchase_order.quantity
    original_product = purchase_order.product
    original_store = purchase_order.store

    serializer = PurchaseOrderCreateUpdateSerializer(purchase_order, data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    updated_product_id = validated_data.get('product_id')
    updated_store_id = validated_data.get('store_id')
    updated_status = validated_data.get('status')
    updated_quantity = validated_data.get('quantity')

    try:
        with transaction.atomic():
            if original_status == 'Pending' and updated_status == 'Completed':
                _update_inventory_on_completion(validated_data)

            elif original_status == 'Completed' and updated_status == 'Pending':
                _revert_inventory_on_pending(original_product, original_store, original_quantity)

            elif original_status == 'Completed' and updated_status == 'Completed':
                if original_product.id != updated_product_id or original_store.id != updated_store_id:
                    _revert_inventory_on_pending(original_product, original_store, original_quantity)
                    _update_inventory_on_completion(validated_data)
                elif original_quantity != updated_quantity:
                    _adjust_inventory_quantity(validated_data, original_quantity)

            # Save the updated purchase order after successful inventory operations
            updated_purchase_order = serializer.save()

    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)



def _update_inventory_on_completion(validated_data):
    product_id = validated_data.get('product_id')
    store_id = validated_data.get('store_id')
    quantity = validated_data.get('quantity')
    name = validated_data.get('name')

    try:
        inventory = Inventory.objects.get(
            product=product_id,
            store=store_id
        )
        inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
        new_in_stock = inventory_in_stock + quantity

        # Check if new_in_stock exceeds max_stock, if max_stock is set
        if inventory.max_stock and inventory.max_stock.isdigit():
            max_stock = int(inventory.max_stock)
            if new_in_stock > max_stock:
                raise ValueError(
                    f"Cannot add {quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
                )

        inventory.in_stock = str(new_in_stock)
        inventory.save()
    except Inventory.DoesNotExist:
        Inventory.objects.create(
            in_stock=str(quantity),
            product_id=product_id,
            store_id=store_id,
            code=name
        )


def _adjust_inventory_quantity(validated_data, original_quantity):
    product_id = validated_data.get('product_id')
    store_id = validated_data.get('store_id')
    quantity = validated_data.get('quantity')

    try:
        inventory = Inventory.objects.get(
            product=product_id,
            store=store_id
        )
        inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
        new_in_stock = inventory_in_stock + quantity - original_quantity

        # Check if new_in_stock exceeds max_stock, if max_stock is set
        if inventory.max_stock and inventory.max_stock.isdigit():
            max_stock = int(inventory.max_stock)
            if new_in_stock > max_stock:
                raise ValueError(
                    f"Cannot adjust inventory by {quantity - original_quantity}. "
                    f"Maximum stock level of {max_stock} would be exceeded."
                )

        inventory.in_stock = str(new_in_stock)
        inventory.save()
    except Inventory.DoesNotExist:
        pass  # Inventory should exist, but in case it doesn't, just continue


def _revert_inventory_on_pending(product, store, quantity):
    try:
        inventory = Inventory.objects.get(
            product=product,
            store=store
        )
        inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
        new_in_stock = inventory_in_stock - quantity

        # Check if new_in_stock exceeds max_stock, if max_stock is set
        if inventory.max_stock and inventory.max_stock.isdigit():
            max_stock = int(inventory.max_stock)
            if new_in_stock > max_stock:
                raise ValueError(
                    f"Cannot revert inventory by {quantity}. Maximum stock level of {max_stock} would be exceeded."
                )

        # Only save if there is no error
        inventory.in_stock = str(new_in_stock)
        inventory.save()
    except Inventory.DoesNotExist:
        pass  # Inventory should exist, but in case it doesn't, just continue


# def _update_inventory_on_completion(purchase_order):
#     try:
#         inventory = Inventory.objects.get(
#             product=purchase_order.product,
#             store=purchase_order.store
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         new_in_stock = inventory_in_stock + purchase_order.quantity

#         # Check if new_in_stock exceeds max_stock, if max_stock is set
#         if inventory.max_stock and inventory.max_stock.isdigit():
#             max_stock = int(inventory.max_stock)
#             if new_in_stock > max_stock:
#                 raise ValueError(
#                     f"Cannot add {purchase_order.quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
#                 )

#         inventory.in_stock = str(new_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         Inventory.objects.create(
#             in_stock=str(purchase_order.quantity),
#             product=purchase_order.product,
#             store=purchase_order.store,
#             code=purchase_order.name
#         )


# def _update_inventory_on_completion(purchase_order):
#     try:
#         inventory = Inventory.objects.get(
#             product=purchase_order.product,
#             store=purchase_order.store
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         new_in_stock = inventory_in_stock + purchase_order.quantity

#         # Check if new_in_stock exceeds max_stock, if max_stock is set
#         if inventory.max_stock and inventory.max_stock.isdigit():
#             max_stock = int(inventory.max_stock)
#             if new_in_stock > max_stock:
#                 raise ValueError(
#                     f"Cannot add {purchase_order.quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
#                 )

#         inventory.in_stock = str(new_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         Inventory.objects.create(
#             in_stock=str(purchase_order.quantity),
#             product=purchase_order.product,
#             store=purchase_order.store,
#             code=purchase_order.name
#         )


# def _adjust_inventory_quantity(purchase_order, original_quantity):
#     try:
#         inventory = Inventory.objects.get(
#             product=purchase_order.product,
#             store=purchase_order.store
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         new_in_stock = inventory_in_stock + purchase_order.quantity - original_quantity

#         # Check if new_in_stock exceeds max_stock, if max_stock is set
#         if inventory.max_stock and inventory.max_stock.isdigit():
#             max_stock = int(inventory.max_stock)
#             if new_in_stock > max_stock:
#                 raise ValueError(
#                     f"Cannot adjust inventory by {purchase_order.quantity - original_quantity}. "
#                     f"Maximum stock level of {max_stock} would be exceeded."
#                 )

#         inventory.in_stock = str(new_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         pass  # Inventory should exist, but in case it doesn't, just continue



# def _update_inventory_on_completion(purchase_order):
#     try:
#         inventory = Inventory.objects.get(
#             product=purchase_order.product,
#             store=purchase_order.store
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         inventory_in_stock += purchase_order.quantity
#         inventory.in_stock = str(inventory_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         Inventory.objects.create(
#             in_stock=str(purchase_order.quantity),
#             product=purchase_order.product,
#             store=purchase_order.store,
#             code=purchase_order.name
#         )


# def _adjust_inventory_quantity(purchase_order, original_quantity):
#     try:
#         inventory = Inventory.objects.get(
#             product=purchase_order.product,
#             store=purchase_order.store
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         inventory_in_stock += purchase_order.quantity - original_quantity
#         inventory.in_stock = str(inventory_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         pass  # Inventory should exist, but in case it doesn't, just continue


# @api_view(['PUT'])
# def update_purchase_order(request, purchase_order_id):
#     try:
#         purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
#     except PurchaseOrder.DoesNotExist:
#         return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

#     # Save the original status and quantity before update
#     original_status = purchase_order.status
#     original_quantity = purchase_order.quantity

#     serializer = PurchaseOrderCreateUpdateSerializer(purchase_order, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     updated_purchase_order = serializer.save()

#     if original_status == 'Pending' and updated_purchase_order.status == 'Completed':
#         # Handle status change from Pending to Completed
#         try:
#             inventory = Inventory.objects.get(
#                 product=updated_purchase_order.product,
#                 store=updated_purchase_order.store
#             )
#             inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#             inventory_in_stock += updated_purchase_order.quantity
#             inventory.in_stock = str(inventory_in_stock)
#             inventory.save()
#         except Inventory.DoesNotExist:
#             Inventory.objects.create(
#                 in_stock=str(updated_purchase_order.quantity),
#                 product=updated_purchase_order.product,
#                 store=updated_purchase_order.store,
#                 code=updated_purchase_order.name
#             )

#     elif original_status == 'Completed' and updated_purchase_order.status == 'Pending':
#         # Handle status change from Completed to Pending
#         try:
#             inventory = Inventory.objects.get(
#                 product=updated_purchase_order.product,
#                 store=updated_purchase_order.store
#             )
#             inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#             inventory_in_stock -= original_quantity
#             inventory.in_stock = str(inventory_in_stock)
#             inventory.save()
#         except Inventory.DoesNotExist:
#             pass  # Inventory should exist, but in case it doesn't, just continue

#     elif original_status == 'Completed' and updated_purchase_order.status == 'Completed':
#         # Handle changes in quantity while status is Completed
#         try:
#             inventory = Inventory.objects.get(
#                 product=updated_purchase_order.product,
#                 store=updated_purchase_order.store
#             )
#             inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#             inventory_in_stock += updated_purchase_order.quantity - original_quantity
#             inventory.in_stock = str(inventory_in_stock)
#             inventory.save()
#         except Inventory.DoesNotExist:
#             pass  # Inventory should exist, but in case it doesn't, just continue

#     return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['DELETE'])
def delete_purchase_order(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        purchase_order.delete()
    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except ProtectedError as e:
        # Extract the related instances causing the ProtectedError
        related_objects = e.protected_objects

        # Extracting the IDs of related objects
        related_ids = [obj.id for obj in related_objects]

        # Get the original error message
        original_message = str(e)

        # Find the part of the message containing the related objects (e.g., "<PurchaseOrder: hj6h5n>")
        start_idx = original_message.find("{")
        end_idx = original_message.find("}") + 1

        # Replace that part with the related IDs
        if start_idx != -1 and end_idx != -1:
            modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
        else:
            modified_message = original_message

        return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
    # except ProtectedError as e:
    #     # Return a more detailed error message
    #     return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()

@api_view(['DELETE'])
def delete_purchase_order_stock(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        product = purchase_order.product
        store = purchase_order.store
        quantity = purchase_order.quantity

        # Attempt to find the corresponding Inventory record
        try:
            inventory = Inventory.objects.get(product=product, store=store)
            inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0

            # Subtract the purchase order quantity from the in_stock
            inventory_in_stock -= quantity

            # Ensure in_stock doesn't go negative
            inventory.in_stock = str(max(inventory_in_stock, 0))
            inventory.save()

        except Inventory.DoesNotExist:
            pass  # If no inventory record exists, do nothing

        purchase_order.delete()

    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    except ProtectedError as e:
        related_objects = e.protected_objects
        related_ids = [obj.id for obj in related_objects]
        original_message = str(e)
        start_idx = original_message.find("{")
        end_idx = original_message.find("}") + 1

        if start_idx != -1 and end_idx != -1:
            modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
        else:
            modified_message = original_message

        return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)

    return Response()



@api_view(['GET'])
def get_purchase_order_by_id(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSinglePurchaseOrderSerializer(purchase_order)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_purchase_orders(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        purchase_orders = PurchaseOrder.objects.filter(id__in=request.data)
        if not purchase_orders.exists():
            return Response({"detail": "None of the purchase_orders found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the purchase_orders
        try:
            count, _ = purchase_orders.delete()
            return Response({"detail": f"{count} purchase_orders deleted successfully."}, status=status.HTTP_200_OK)
        except ProtectedError as e:
            # Extract the related instances causing the ProtectedError
            related_objects = e.protected_objects

            # Extracting the IDs of related objects
            related_ids = [obj.id for obj in related_objects]

            # Get the original error message
            original_message = str(e)

            # Find the part of the message containing the related objects (e.g., "<Product: hj6h5n>")
            start_idx = original_message.find("{")
            end_idx = original_message.find("}") + 1

            # Replace that part with the related IDs
            if start_idx != -1 and end_idx != -1:
                modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
            else:
                modified_message = original_message

            return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)