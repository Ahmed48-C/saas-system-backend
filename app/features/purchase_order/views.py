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
from app.features.inventory_log.services import InventoryLogService

# Create your views here.

from app.features.purchase_order.models import PurchaseOrder, PurchaseStatus
from app.features.inventory.models import Inventory
from app.features.balance.models import Balance
from app.common.json_utils import JsonUtils
from app.features.inventory_log.models import ActionLog, AutoNoteLog


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
#     validated_data = serializer.validated_data

#     status_order = validated_data.get('status')
#     quantity = validated_data.get('quantity')
#     store_id = validated_data.get('store_id')
#     product_id = validated_data.get('product_id')
#     balance_id = validated_data.get('balance_id')
#     total = validated_data.get('total')  # Assuming total is provided in the request data

#     # Fetch the balance associated with the balance_id
#     try:
#         balance = Balance.objects.get(id=balance_id)
#     except Balance.DoesNotExist:
#         return Response({
#             "detail": "Balance not found."
#         }, status=status.HTTP_404_NOT_FOUND)

#     # Check if the total minus the balance amount would go negative
#     if balance.amount - total < 0:
#         return Response({
#             "detail": "The total amount exceeds the available balance. Please adjust the order or add funds."
#         }, status=status.HTTP_400_BAD_REQUEST)

#     if status_order == 'Completed':
#         try:
#             inventory = Inventory.objects.get(
#                 product=product_id,
#                 store=store_id
#             )

#             # Convert inventory.in_stock to integer if it's a string
#             inventory_in_stock = int(inventory.in_stock) if inventory.in_stock and inventory.in_stock.isdigit() else 0
#             new_in_stock = inventory_in_stock + quantity

#             # Debugging outputs
#             print(f"Inventory In Stock: {inventory_in_stock}")
#             print(f"New In Stock: {new_in_stock}")

#             # Check if new_in_stock exceeds max_stock, if max_stock is set
#             if inventory.max_stock and inventory.max_stock.isdigit():
#                 max_stock = int(inventory.max_stock)
#                 print(f"Max Stock: {max_stock}")
#                 if new_in_stock > max_stock:
#                     return Response({
#                         "detail": f"Cannot add {quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
#                     }, status=status.HTTP_400_BAD_REQUEST)

#             # Save new_in_stock back as string
#             inventory.in_stock = str(new_in_stock)
#             inventory.save()

#         except Inventory.DoesNotExist:
#             try:
#                 Inventory.objects.create(
#                     in_stock=str(quantity),  # Save as string
#                     product_id=product_id,
#                     store_id=store_id,
#                     code=validated_data.get('code')
#                 )
#             except Exception as e:
#                 # If creation fails, return a meaningful error message
#                 return Response({
#                     "detail": f"Failed to create inventory: {str(e)}"
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     # If the balance is sufficient, subtract the total from the balance amount
#     balance.amount -= total
#     balance.save()
#     # Save the purchase order only after the inventory and balance checks
#     purchase_order = serializer.save()

#     return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_purchase_order(request):
    serializer = PurchaseOrderCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.db import transaction

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
#     original_total = purchase_order.total  # Assuming there's a total field in the purchase order

#     serializer = PurchaseOrderCreateUpdateSerializer(purchase_order, data=request.data)
#     serializer.is_valid(raise_exception=True)

#     validated_data = serializer.validated_data
#     updated_product_id = validated_data.get('product_id')
#     updated_store_id = validated_data.get('store_id')
#     updated_status = validated_data.get('status')
#     updated_quantity = validated_data.get('quantity')
#     updated_total = validated_data.get('total')  # Assuming you're updating total

#     balance_id = validated_data.get('balance_id')  # Assuming you pass balance ID
#     balance = Balance.objects.get(id=balance_id)  # Fetch balance object

#     try:
#         with transaction.atomic():
#             # Handle inventory update based on status changes
#             if original_status == 'Pending' and updated_status == 'Completed':
#                 _update_inventory_on_completion(validated_data)

#             elif original_status == 'Completed' and updated_status == 'Pending':
#                 _revert_inventory_on_pending(original_product, original_store, original_quantity)

#             elif original_status == 'Completed' and updated_status == 'Completed':
#                 if original_product.id != updated_product_id or original_store.id != updated_store_id:
#                     _revert_inventory_on_pending(original_product, original_store, original_quantity)
#                     _update_inventory_on_completion(validated_data)
#                 elif original_quantity != updated_quantity:
#                     _adjust_inventory_quantity(validated_data, original_quantity)

#             # Handle balance check
#             balance_adjustment = updated_total - original_total  # Difference in total amount

#             # If the new balance would go negative, raise an error
#             if balance.amount - balance_adjustment < 0:
#                 return Response({
#                     "detail": "Insufficient balance to complete the purchase order."
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # If balance is sufficient, update balance amount
#             balance.amount -= balance_adjustment
#             balance.save()

#             # Save the updated purchase order after successful inventory and balance operations
#             updated_purchase_order = serializer.save()

#     except ValueError as e:
#         return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     return Response(serializer.data, status=status.HTTP_200_OK)


# def _update_inventory_on_completion(validated_data):
#     product_id = validated_data.get('product_id')
#     store_id = validated_data.get('store_id')
#     quantity = validated_data.get('quantity')
#     code = validated_data.get('code')

#     try:
#         inventory = Inventory.objects.get(
#             product=product_id,
#             store=store_id
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         new_in_stock = inventory_in_stock + quantity

#         # Check if new_in_stock exceeds max_stock, if max_stock is set
#         if inventory.max_stock and inventory.max_stock.isdigit():
#             max_stock = int(inventory.max_stock)
#             if new_in_stock > max_stock:
#                 raise ValueError(
#                     f"Cannot add {quantity} to inventory. Maximum stock level of {max_stock} would be exceeded."
#                 )

#         inventory.in_stock = str(new_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         Inventory.objects.create(
#             in_stock=str(quantity),
#             product_id=product_id,
#             store_id=store_id,
#             code=code
#         )


# def _adjust_inventory_quantity(validated_data, original_quantity):
#     product_id = validated_data.get('product_id')
#     store_id = validated_data.get('store_id')
#     quantity = validated_data.get('quantity')

#     try:
#         inventory = Inventory.objects.get(
#             product=product_id,
#             store=store_id
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         new_in_stock = inventory_in_stock + quantity - original_quantity

#         # Check if new_in_stock exceeds max_stock, if max_stock is set
#         if inventory.max_stock and inventory.max_stock.isdigit():
#             max_stock = int(inventory.max_stock)
#             if new_in_stock > max_stock:
#                 raise ValueError(
#                     f"Cannot adjust inventory by {quantity - original_quantity}. "
#                     f"Maximum stock level of {max_stock} would be exceeded."
#                 )

#         inventory.in_stock = str(new_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         pass  # Inventory should exist, but in case it doesn't, just continue


# def _revert_inventory_on_pending(product, store, quantity):
#     try:
#         inventory = Inventory.objects.get(
#             product=product,
#             store=store
#         )
#         inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
#         new_in_stock = inventory_in_stock - quantity

#         # Check if new_in_stock exceeds max_stock, if max_stock is set
#         if inventory.max_stock and inventory.max_stock.isdigit():
#             max_stock = int(inventory.max_stock)
#             if new_in_stock > max_stock:
#                 raise ValueError(
#                     f"Cannot revert inventory by {quantity}. Maximum stock level of {max_stock} would be exceeded."
#                 )

#         # Only save if there is no error
#         inventory.in_stock = str(new_in_stock)
#         inventory.save()
#     except Inventory.DoesNotExist:
#         pass  # Inventory should exist, but in case it doesn't, just continue


@api_view(['PUT'])
def update_purchase_order(request, purchase_order_id):
    try:
        # Retrieve the purchase order by ID
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    # Pass the retrieved purchase order and the request data to the serializer
    serializer = PurchaseOrderCreateUpdateSerializer(purchase_order, data=request.data)

    # Validate the data
    serializer.is_valid(raise_exception=True)

    # Save the updates through the serializer (which handles inventory and balance logic)
    updated_purchase_order = serializer.save()

    # Return the updated purchase order data in the response
    return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['DELETE'])
# def delete_purchase_order(request, purchase_order_id):
#     try:
#         purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
#         purchase_order.delete()
#     except PurchaseOrder.DoesNotExist:
#         return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
#     except ProtectedError as e:
#         # Extract the related instances causing the ProtectedError
#         related_objects = e.protected_objects

#         # Extracting the IDs of related objects
#         related_ids = [obj.id for obj in related_objects]

#         # Get the original error message
#         original_message = str(e)

#         # Find the part of the message containing the related objects (e.g., "<PurchaseOrder: hj6h5n>")
#         start_idx = original_message.find("{")
#         end_idx = original_message.find("}") + 1

#         # Replace that part with the related IDs
#         if start_idx != -1 and end_idx != -1:
#             modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
#         else:
#             modified_message = original_message

#         return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
#     # except ProtectedError as e:
#     #     # Return a more detailed error message
#     #     return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     return Response()

@api_view(['DELETE'])
def delete_purchase_order(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)

        if purchase_order.status.upper() == "COMPLETED":
            # Adjust stock based on related PurchaseItems
            for item in purchase_order.items.all():
                try:
                    inventory = Inventory.objects.get(product=item.product, store=purchase_order.store, supplier=purchase_order.supplier)
                    # inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
                    inventory_in_stock = int(inventory.in_stock or 0)
                    # Adjust inventory stock
                    current_stock = int(inventory.in_stock or 0)
                    inventory_in_stock -= item.quantity
                    inventory.in_stock = str(max(inventory_in_stock, 0))
                    inventory.save()

                    InventoryLogService().add_inventory_log(
                        userprofile_id = None, #TODO
                        product_id = item.product.id,
                        store_id = purchase_order.store.id,
                        stock = current_stock,
                        action = ActionLog.MINUS,
                        auto_generated_note = AutoNoteLog.DELETE_PURCHASE_ORDER,
                        stock_before_action = current_stock,
                        stock_after_action = inventory.in_stock,
                    )
                except Inventory.DoesNotExist:
                    pass  # Handle missing inventory if necessary
        # Adjust stock based on related PurchaseItems
        # for item in purchase_order.items.all():
        #     try:
        #         inventory = Inventory.objects.get(product=item.product, store=purchase_order.store, supplier=purchase_order.supplier)
        #         # inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
        #         inventory_in_stock = int(inventory.in_stock or 0)
        #         # Adjust inventory stock
        #         inventory_in_stock -= item.quantity
        #         inventory.in_stock = str(max(inventory_in_stock, 0))
        #         inventory.save()
        #     except Inventory.DoesNotExist:
        #         pass  # Handle missing inventory if necessary

        purchase_order.delete()

    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    # except ProtectedError as e:
    #     # Handle ProtectedError logic (as before)
    #     related_objects = e.protected_objects
    #     related_ids = [obj.id for obj in related_objects]
    #     original_message = str(e)
    #     start_idx = original_message.find("{")
    #     end_idx = original_message.find("}") + 1

    #     if start_idx != -1 and end_idx != -1:
    #         modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
    #     else:
    #         modified_message = original_message

    #     return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
    except ProtectedError as e:
        # Return a more detailed error message
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()


# @api_view(['DELETE'])
# def delete_purchase_order_stock(request, purchase_order_id):
#     try:
#         purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
#         product = purchase_order.product
#         store = purchase_order.store
#         quantity = purchase_order.quantity

#         # Attempt to find the corresponding Inventory record
#         try:
#             inventory = Inventory.objects.get(product=product, store=store)
#             inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0

#             # Subtract the purchase order quantity from the in_stock
#             inventory_in_stock -= quantity

#             # Ensure in_stock doesn't go negative
#             inventory.in_stock = str(max(inventory_in_stock, 0))
#             inventory.save()

#         except Inventory.DoesNotExist:
#             pass  # If no inventory record exists, do nothing

#         purchase_order.delete()

#     except PurchaseOrder.DoesNotExist:
#         return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#     except ProtectedError as e:
#         related_objects = e.protected_objects
#         related_ids = [obj.id for obj in related_objects]
#         original_message = str(e)
#         start_idx = original_message.find("{")
#         end_idx = original_message.find("}") + 1

#         if start_idx != -1 and end_idx != -1:
#             modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
#         else:
#             modified_message = original_message

#         return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)

#     return Response()


@api_view(['DELETE'])
def delete_purchase_order_stock(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        
        if purchase_order.status.upper() == "COMPLETED":
            # Adjust stock for each PurchaseItem
            for item in purchase_order.items.all():
                product = item.product
                store = purchase_order.store
                supplier = purchase_order.supplier
                quantity = item.quantity

                try:
                    inventory = Inventory.objects.get(product=product, store=store, supplier=supplier)
                    # inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
                    inventory_in_stock = int(inventory.in_stock or 0)
                    current_stock = int(inventory.in_stock or 0)
                    # Subtract the purchase item quantity from the in_stock
                    inventory_in_stock -= quantity

                    # Ensure in_stock doesn't go negative
                    inventory.in_stock = str(max(inventory_in_stock, 0))
                    inventory.save()

                    InventoryLogService().add_inventory_log(
                        userprofile_id = None, #TODO
                        product_id = product.id,
                        store_id = store.id,
                        stock = current_stock,
                        action = ActionLog.MINUS,
                        auto_generated_note = AutoNoteLog.DELETE_PURCHASE_ORDER,
                        stock_before_action = current_stock,
                        stock_after_action = inventory.in_stock,
                    )
                except Inventory.DoesNotExist:
                    pass  # If no inventory record exists, do nothing

        purchase_order.delete()

    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # except ProtectedError as e:
    #     related_objects = e.protected_objects
    #     related_ids = [obj.id for obj in related_objects]
    #     original_message = str(e)
    #     start_idx = original_message.find("{")
    #     end_idx = original_message.find("}") + 1

    #     if start_idx != -1 and end_idx != -1:
    #         modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
    #     else:
    #         modified_message = original_message

    #     return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
    except ProtectedError as e:
        # Return a more detailed error message
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()



@api_view(['GET'])
def get_purchase_order_by_id(request, purchase_order_id):
    try:
        if purchase_order_id == "last":
            # Retrieve the last purchase order by creation date or ID
            purchase_order = PurchaseOrder.objects.latest('id')  # Or use .last() if ordering is different
        else:
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    except PurchaseOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSinglePurchaseOrderSerializer(purchase_order)
    return Response(serializer.data)


# @api_view(['DELETE'])
# def delete_purchase_orders(request):
#     # Ensure the request body contains a list of IDs
#     if not isinstance(request.data, list):
#         return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         purchase_orders = PurchaseOrder.objects.filter(id__in=request.data)
#         if not purchase_orders.exists():
#             return Response({"detail": "None of the purchase_orders found."}, status=status.HTTP_404_NOT_FOUND)

#         # Attempt to delete the purchase_orders
#         try:
#             count, _ = purchase_orders.delete()
#             return Response({"detail": f"{count} purchase_orders deleted successfully."}, status=status.HTTP_200_OK)
#         except ProtectedError as e:
#             # Extract the related instances causing the ProtectedError
#             related_objects = e.protected_objects

#             # Extracting the IDs of related objects
#             related_ids = [obj.id for obj in related_objects]

#             # Get the original error message
#             original_message = str(e)

#             # Find the part of the message containing the related objects (e.g., "<Product: hj6h5n>")
#             start_idx = original_message.find("{")
#             end_idx = original_message.find("}") + 1

#             # Replace that part with the related IDs
#             if start_idx != -1 and end_idx != -1:
#                 modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
#             else:
#                 modified_message = original_message

#             return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_purchase_orders(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        purchase_orders = PurchaseOrder.objects.filter(id__in=request.data)
        if not purchase_orders.exists():
            return Response({"detail": "None of the purchase_orders found."}, status=status.HTTP_404_NOT_FOUND)

        # Adjust stock for each purchase order's items
        # for purchase_order in purchase_orders:
        #     for item in purchase_order.items.all():
        #         try:
        #             inventory = Inventory.objects.get(product=item.product, store=purchase_order.store)
        #             # inventory_in_stock = int(inventory.in_stock) if inventory.in_stock.isdigit() else 0
        #             inventory_in_stock = int(inventory.in_stock or 0)
        #             inventory_in_stock -= item.quantity
        #             inventory.in_stock = str(max(inventory_in_stock, 0))
        #             inventory.save()
        #         except Inventory.DoesNotExist:
        #             pass  # Handle missing inventory if necessary

        # Attempt to delete the purchase_orders
        try:
            count, _ = purchase_orders.delete()
            return Response({"detail": f"{count} purchase_orders deleted successfully."}, status=status.HTTP_200_OK)
        # except ProtectedError as e:
        #     # Handle ProtectedError logic (as before)
        #     related_objects = e.protected_objects
        #     related_ids = [obj.id for obj in related_objects]
        #     original_message = str(e)
        #     start_idx = original_message.find("{")
        #     end_idx = original_message.find("}") + 1

        #     if start_idx != -1 and end_idx != -1:
        #         modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
        #     else:
        #         modified_message = original_message

        #     return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
        except ProtectedError as e:
            # Return a more detailed error message
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_purchase_status_choices(request):
    obj = JsonUtils.get_choices_as_list(PurchaseStatus.choices)
    return JsonResponse(obj, safe=False)