from django.shortcuts import render
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.courier.serializers import (
    CourierGetAllSerializer,
    CourierCreateUpdateSerializer,
    GetSingleCourierSerializer,
)

# Create your views here.

from app.features.courier.models import Courier, VehicleTypes
from app.common.json_utils import JsonUtils


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_courier(request):
    records, actual_total_count = Courier.objects.get_all_by_limit(request)
    serializer = CourierGetAllSerializer(records, many=True)

    json_obj = Courier.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_courier(request):
    serializer = CourierCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_courier(request, courier_id):
    try:
        courier = Courier.objects.get(id=courier_id)
    except Courier.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourierCreateUpdateSerializer(courier, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_courier(request, courier_id):
    try:
        courier = Courier.objects.get(id=courier_id)
        courier.soft_delete()
    except Courier.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_courier_by_id(request, courier_id):
    try:
        courier = Courier.objects.get(id=courier_id)
    except Courier.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleCourierSerializer(courier)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_courier_vehicle_types(request):
    obj = JsonUtils.get_choices_as_list(VehicleTypes.choices)
    return JsonResponse(obj, safe=False)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_couriers(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        couriers = Courier.objects.filter(id__in=request.data)
        if not couriers.exists():
            return Response({"detail": "None of the couriers found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected couriers
        for courier in couriers:
            courier.soft_delete()
        
        return Response({"detail": f"{couriers.count()} couriers deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)