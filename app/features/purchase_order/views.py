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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_purchase_order(request):
    records, actual_total_count = PurchaseOrder.objects.get_all_by_limit(request)
    serializer = PurchaseOrderGetAllSerializer(records, many=True)

    json_obj = PurchaseOrder.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_purchase_order(request):
    serializer = PurchaseOrderCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.db import transaction


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_purchase_order(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)

        if purchase_order.status.upper() == "COMPLETED":
            # Adjust stock based on related PurchaseItems
            for item in purchase_order.items.all():
                try:
                    inventory = Inventory.objects.get(product=item.product, store=purchase_order.store)
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

        purchase_order.soft_delete()

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

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_purchase_order_stock(request, purchase_order_id):
    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        
        if purchase_order.status.upper() == "COMPLETED":
            # Adjust stock for each PurchaseItem
            for item in purchase_order.items.all():
                product = item.product
                store = purchase_order.store
                quantity = item.quantity

                try:
                    inventory = Inventory.objects.get(product=product, store=store)
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

        purchase_order.soft_delete()

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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_purchase_orders(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        purchase_orders = PurchaseOrder.objects.filter(id__in=request.data)
        if not purchase_orders.exists():
            return Response({"detail": "None of the purchase_orders found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected purchase_orders
        for purchase_order in purchase_orders:
            purchase_order.soft_delete()

        return Response({"detail": f"{purchase_orders.count()} purchase orders deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_purchase_status_choices(request):
    obj = JsonUtils.get_choices_as_list(PurchaseStatus.choices)
    return JsonResponse(obj, safe=False)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_last_30_days_purchase_orders(request):
    from datetime import datetime, timedelta
    from django.db.models import Sum
    from django.utils import timezone
    
    # Calculate the date 30 days ago from today
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get completed purchase orders for last 30 days
    completed_orders = PurchaseOrder.objects.filter(
        status=PurchaseStatus.COMPLETED,
        completed_at__gte=thirty_days_ago
    ).order_by('-completed_at')
    
    # Get pending purchase orders for last 30 days
    pending_orders = PurchaseOrder.objects.filter(
        status=PurchaseStatus.PENDING,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')
    
    # Calculate total amounts
    completed_total = completed_orders.aggregate(total=Sum('total'))['total'] or 0
    pending_total = pending_orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Prepare orders data
    completed_list = [{
        'total': order.total,
        'completed_at': order.completed_at
    } for order in completed_orders]
    
    pending_list = [{
        'total': order.total,
        'created_at': order.created_at
    } for order in pending_orders]
    
    return Response({
        'completed_total': completed_total,
        'pending_total': pending_total,
        'completed_orders': completed_list,
        'pending_orders': pending_list
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_month_purchase_orders(request):
    from datetime import datetime
    from django.db.models import Sum
    from django.utils import timezone
    
    # Get the current date
    today = timezone.now()
    # Get the first day of the current month
    first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get completed purchase orders for current month
    completed_orders = PurchaseOrder.objects.filter(
        status=PurchaseStatus.COMPLETED,
        completed_at__year=today.year,
        completed_at__month=today.month
    ).order_by('-completed_at')
    
    # Get pending purchase orders for current month
    pending_orders = PurchaseOrder.objects.filter(
        status=PurchaseStatus.PENDING,
        created_at__year=today.year,
        created_at__month=today.month
    ).order_by('-created_at')
    
    # Calculate total amounts
    completed_total = completed_orders.aggregate(total=Sum('total'))['total'] or 0
    pending_total = pending_orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Prepare orders data
    completed_list = [{
        'total': order.total,
        'completed_at': order.completed_at
    } for order in completed_orders]
    
    pending_list = [{
        'total': order.total,
        'created_at': order.created_at
    } for order in pending_orders]
    
    return Response({
        'completed_total': completed_total,
        'pending_total': pending_total,
        'completed_orders': completed_list,
        'pending_orders': pending_list
    })