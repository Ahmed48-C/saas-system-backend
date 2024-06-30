from django.shortcuts import render

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.operator.serializers import (
    OperatorGetAllSerializer,
    OperatorCreateUpdateSerializer,
    GetSingleOperatorSerializer,
)

# Create your views here.

from app.features.operator.models import Operator


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_operator(request):
    records, actual_total_count = Operator.objects.get_all_by_limit(request)
    serializer = OperatorGetAllSerializer(records, many=True)

    json_obj = Operator.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_operator(request):
    serializer = OperatorCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
def update_operator(request, operator_id):
    try:
        operator = Operator.objects.get(id=operator_id)
    except Operator.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = OperatorCreateUpdateSerializer(operator, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_operator(request, operator_id):
    try:
        operator = Operator.objects.get(id=operator_id)
    except Operator.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    operator.delete()
    return Response()


@api_view(['GET'])
def get_operator_by_id(request, operator_id):
    try:
        operator = Operator.objects.get(id=operator_id)
    except Operator.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleOperatorSerializer(operator)
    return Response(serializer.data)