from django.shortcuts import render

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.inventory.serializers import (
    InventoryGetAllSerializer,
    InventoryCreateUpdateSerializer,
    GetSingleInventorySerializer,
)

# Create your views here.

from app.features.inventory.models import Inventory


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_inventory(request):
    records, actual_total_count = Inventory.objects.get_all_by_limit(request)
    serializer = InventoryGetAllSerializer(records, many=True)

    json_obj = Inventory.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_inventory(request):
    serializer = InventoryCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
def update_inventory(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InventoryCreateUpdateSerializer(inventory, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_inventory(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    inventory.delete()
    return Response()


@api_view(['GET'])
def get_inventory_by_id(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleInventorySerializer(inventory)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_inventories(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve and delete inventories in a batch
    try:
        inventories = Inventory.objects.filter(id__in=request.data)
        if not inventories.exists():
            return Response({"detail": "None of the inventories found."}, status=status.HTTP_404_NOT_FOUND)
        count, _ = inventories.delete()
        return Response({"detail": f"{count} inventories deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)