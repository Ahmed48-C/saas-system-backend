from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    TestSerializer,
    LocationGetAllSerializer,
    LocationCreateUpdateSerializer,
)

# Create your views here.

from .models import TestModel, Location

@api_view(['GET'])
def records_list(request):
    records = TestModel.objects.all()
    serializer = TestSerializer(records, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_all_location(request):
    records = Location.objects.all()
    serializer = LocationGetAllSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_location(request):
    serializer = LocationCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)