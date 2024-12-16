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
    except InventoryLog.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    inventory_log.delete()
    return Response()


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

        # Attempt to delete the inventory_logs
        try:
            count, _ = inventory_logs.delete()
            return Response({"detail": f"{count} inventory_logs deleted successfully."}, status=status.HTTP_200_OK)
        # except ProtectedError as e:
        #     # Extract the related instances causing the ProtectedError
        #     related_objects = e.protected_objects

        #     # Extracting the IDs of related objects
        #     related_ids = [obj.id for obj in related_objects]

        #     # Get the original error message
        #     original_message = str(e)

        #     # Find the part of the message containing the related objects (e.g., "<Product: hj6h5n>")
        #     start_idx = original_message.find("{")
        #     end_idx = original_message.find("}") + 1

        #     # Replace that part with the related IDs
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