from django.shortcuts import render
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.inventory_log.serializers import (
    InventoryLogGetAllSerializer,
    InventoryLogCreateUpdateSerializer,
    GetSingleInventoryLogSerializer,
)

# Create your views here.

from app.features.inventory_log.models import InventoryLog
from app.common.json_utils import JsonUtils


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_inventory_log(request):
    records, actual_total_count = InventoryLog.objects.get_all_by_limit(request)
    serializer = InventoryLogGetAllSerializer(records, many=True)

    json_obj = InventoryLog.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_inventory_log(request):
    serializer = InventoryLogCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_inventory_log(request, inventory_log_id):
    try:
        inventory_log = InventoryLog.objects.get(id=inventory_log_id)
    except InventoryLog.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InventoryLogCreateUpdateSerializer(inventory_log, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_inventory_log(request, inventory_log_id):
    try:
        inventory_log = InventoryLog.objects.get(id=inventory_log_id)
        inventory_log.soft_delete()
    except InventoryLog.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_inventory_log_by_id(request, inventory_log_id):
    try:
        inventory_log = InventoryLog.objects.get(id=inventory_log_id)
    except InventoryLog.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleInventoryLogSerializer(inventory_log)
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_inventory_logs(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        inventory_logs = InventoryLog.objects.filter(id__in=request.data)
        if not inventory_logs.exists():
            return Response({"detail": "None of the inventory_logs found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected inventory_logs
        for inventory_log in inventory_logs:
            inventory_log.soft_delete()

        return Response({"detail": f"{inventory_logs.count()} inventory_logs deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)