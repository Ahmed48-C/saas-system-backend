from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError

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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_inventory(request):
    records, actual_total_count = Inventory.objects.get_all_by_limit(request)
    serializer = InventoryGetAllSerializer(records, many=True)

    json_obj = Inventory.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_inventory(request):
    # TODO
    request.data['userprofile'] = None # current error : AttributeError: 'AnonymousUser' object has no attribute 'userprofile'

    serializer = InventoryCreateUpdateSerializer(data=request.data)

    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_inventory(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    # TODO
    request.data['userprofile'] = None # current error : AttributeError: 'AnonymousUser' object has no attribute 'userprofile'

    serializer = InventoryCreateUpdateSerializer(inventory, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_inventory(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
        inventory.soft_delete()
    except Inventory.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_inventory_by_id(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleInventorySerializer(inventory)
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_inventories(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        inventories = Inventory.objects.filter(id__in=request.data)
        if not inventories.exists():
            return Response({"detail": "None of the inventories found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected inventories
        for inventory in inventories:
            inventory.soft_delete()

        return Response({"detail": f"{inventories.count()} inventories deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_total_stock(request):
    from django.db.models import Sum
    
    total_stock = Inventory.objects.aggregate(total=Sum('in_stock'))['total'] or 0
    
    return Response({
        'total_stock': total_stock
    })