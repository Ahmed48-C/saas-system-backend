from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.client_balance.serializers import (
    ClientBalanceGetAllSerializer,
)

# Create your views here.

from app.features.client_balance.models import ClientBalance


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_client_balance(request):
    records, actual_total_count = ClientBalance.objects.get_all_by_limit(request)
    serializer = ClientBalanceGetAllSerializer(records, many=True)

    json_obj = ClientBalance.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)