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
from app.features.customer.serializers import (
    CustomerGetAllSerializer,
    CustomerCreateUpdateSerializer,
    GetSingleCustomerSerializer,
)

# Create your views here.

from app.features.customer.models import Customer


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_customer(request):
    records, actual_total_count = Customer.objects.get_all_by_limit(request)
    serializer = CustomerGetAllSerializer(records, many=True)

    json_obj = Customer.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_customer(request):
    serializer = CustomerCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomerCreateUpdateSerializer(customer, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.soft_delete()
    except Customer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_customer_by_id(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleCustomerSerializer(customer)
    return Response(serializer.data)


# @api_view(['DELETE'])
# def delete_customers(request):
#     # Ensure the request body contains a list of IDs
#     if not isinstance(request.data, list):
#         return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

#     # Retrieve and delete customers in a batch
#     try:
#         customers = Customer.objects.filter(id__in=request.data)
#         if not customers.exists():
#             return Response({"detail": "None of the customers found."}, status=status.HTTP_404_NOT_FOUND)
#         count, _ = customers.delete()
#         return Response({"detail": f"{count} customers deleted successfully."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_customers(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customers = Customer.objects.filter(id__in=request.data)
        if not customers.exists():
            return Response({"detail": "None of the customers found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected customers
        for customer in customers:
            customer.soft_delete()

        return Response({"detail": f"{customers.count()} customers deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)