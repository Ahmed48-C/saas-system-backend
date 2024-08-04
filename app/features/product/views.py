from django.shortcuts import render

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.product.serializers import (
    ProductGetAllSerializer,
    ProductCreateUpdateSerializer,
    GetSingleProductSerializer,
)

# Create your views here.

from app.features.product.models import Product


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_product(request):
    records, actual_total_count = Product.objects.get_all_by_limit(request)
    serializer = ProductGetAllSerializer(records, many=True)

    json_obj = Product.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_product(request):
    serializer = ProductCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
def update_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductCreateUpdateSerializer(product, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response()


@api_view(['GET'])
def get_product_by_id(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleProductSerializer(product)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_products(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve and delete products in a batch
    try:
        products = Product.objects.filter(id__in=request.data)
        if not products.exists():
            return Response({"detail": "None of the products found."}, status=status.HTTP_404_NOT_FOUND)
        count, _ = products.delete()
        return Response({"detail": f"{count} products deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)