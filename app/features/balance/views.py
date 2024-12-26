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
from app.features.balance.serializers import (
    BalanceGetAllSerializer,
    BalanceCreateUpdateSerializer,
    GetSingleBalanceSerializer,
)

# Create your views here.

from app.features.balance.models import Balance

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_balance(request):
    records, actual_total_count = Balance.objects.get_all_by_limit(request) #Balance.objects.all()
    serializer = BalanceGetAllSerializer(records, many=True)

    json_obj = Balance.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_balance(request):
    serializer = BalanceCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_balance(request, balance_id):
    try:
        balance = Balance.objects.get(id=balance_id)
    except Balance.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BalanceCreateUpdateSerializer(balance, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_balance(request, balance_id):
    try:
        balance = Balance.objects.get(id=balance_id)
        balance.soft_delete()
    except Balance.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_balance_by_id(request, balance_id):
    try:
        balance = Balance.objects.get(id=balance_id)
    except Balance.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleBalanceSerializer(balance)
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_balances(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        balances = Balance.objects.filter(id__in=request.data)
        if not balances.exists():
            return Response({"detail": "None of the balances found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected balances
        for balance in balances:
            balance.soft_delete()

        return Response({"detail": f"{balances.count()} balances deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_total_balance(request):
    from django.db.models import Sum
    
    total_balance = Balance.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    return Response({
        'total_balance': total_balance
    })