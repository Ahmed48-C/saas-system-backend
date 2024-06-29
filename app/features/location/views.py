from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.features.location.serializers import (
    TestSerializer,
    LocationGetAllSerializer,
    LocationCreateUpdateSerializer,
    GetSingleLocationSerializer,
)

# Create your views here.

from app.features.location.models import TestModel, Location

@api_view(['GET'])
def records_list(request):
    records = TestModel.objects.all()
    serializer = TestSerializer(records, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_all_location(request):
    records, actual_total_count = Location.objects.get_all_by_limit(request) #Location.objects.all()
    serializer = LocationGetAllSerializer(records, many=True)

    json_obj = Location.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_location(request):
    serializer = LocationCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
def update_location(request, location_id):
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocationCreateUpdateSerializer(location, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_location(request, location_id):
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    location.delete()
    return Response()


@api_view(['GET'])
def get_location_by_id(request, location_id):
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleLocationSerializer(location)
    return Response(serializer.data)