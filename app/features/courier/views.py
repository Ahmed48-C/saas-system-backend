from django.shortcuts import render

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

from app.features.courier.models import Courier


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_courier(request):
    records, actual_total_count = Courier.objects.get_all_by_limit(request)
    serializer = CourierGetAllSerializer(records, many=True)

    json_obj = Courier.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_courier(request):
    serializer = CourierCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
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
def delete_courier(request, courier_id):
    try:
        courier = Courier.objects.get(id=courier_id)
    except Courier.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    courier.delete()
    return Response()


@api_view(['GET'])
def get_courier_by_id(request, courier_id):
    try:
        courier = Courier.objects.get(id=courier_id)
    except Courier.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleCourierSerializer(courier)
    return Response(serializer.data)