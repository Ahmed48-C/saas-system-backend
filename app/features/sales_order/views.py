from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from app.features.sales_order.serializers import (
    SalesOrderGetAllSerializer,
    SalesOrderCreateUpdateSerializer,
    GetSingleSalesOrderSerializer,
)

# Create your views here.

from app.features.sales_order.models import SalesOrder, SalesStatus
from app.features.inventory.models import Inventory
from app.features.balance.models import Balance
from app.common.json_utils import JsonUtils



@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_sales_orders(request):
    records, actual_total_count = SalesOrder.objects.get_all_by_limit(request)
    serializer = SalesOrderGetAllSerializer(records, many=True)

    json_obj = SalesOrder.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)




@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_sales_order_by_id(request, sales_order_id):
    try:
        if sales_order_id == "last":
            # Retrieve the last sales order by creation date or ID
            sales_order = SalesOrder.objects.latest('id')  # Or use .last() if ordering is different
        else:
            sales_order = SalesOrder.objects.get(id=sales_order_id)
    except SalesOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleSalesOrderSerializer(sales_order)
    return Response(serializer.data)



@api_view(['POST'])
def create_sales_order(request):
    serializer = SalesOrderCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
def update_sales_order(request, sales_order_id):
    try:
        # Retrieve the sales order by ID
        sales_order = SalesOrder.objects.get(id=sales_order_id)
    except SalesOrder.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    # Pass the retrieved sales order and the request data to the serializer
    serializer = SalesOrderCreateUpdateSerializer(sales_order, data=request.data)

    # Validate the data
    serializer.is_valid(raise_exception=True)

    # Save the updates through the serializer (which handles inventory and balance logic)
    updated_sales_order = serializer.save()

    # Return the updated sales order data in the response
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_sales_order(request, sales_order_id):
    try:
        sales_order = SalesOrder.objects.get(id=sales_order_id)
        sales_order.delete()
    except SalesOrder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except ProtectedError as e:
        # Return a more detailed error message
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()


@api_view(['DELETE'])
def delete_sales_orders(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sales_orders = SalesOrder.objects.filter(id__in=request.data)
        if not sales_orders.exists():
            return Response({"detail": "None of the sales_orders found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the sales_orders
        try:
            count, _ = sales_orders.delete()
            return Response({"detail": f"{count} sales_orders deleted successfully."}, status=status.HTTP_200_OK)
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
def get_sales_status_choices(request):
    obj = JsonUtils.get_choices_as_list(SalesStatus.choices)
    return JsonResponse(obj, safe=False)