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
from app.features.supplier.serializers import (
    SupplierGetAllSerializer,
    SupplierCreateUpdateSerializer,
    GetSingleSupplierSerializer,
)

# Create your views here.

from app.features.supplier.models import Supplier


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_supplier(request):
    records, actual_total_count = Supplier.objects.get_all_by_limit(request)
    serializer = SupplierGetAllSerializer(records, many=True)

    json_obj = Supplier.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_supplier(request):
    serializer = SupplierCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_supplier(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SupplierCreateUpdateSerializer(supplier, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_supplier(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.delete()
    except Supplier.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    # except ProtectedError as e:
    #     # Extract the related instances causing the ProtectedError
    #     related_objects = e.protected_objects

    #     # Extracting the IDs of related objects
    #     related_ids = [obj.id for obj in related_objects]

    #     # Get the original error message
    #     original_message = str(e)

    #     # Find the part of the message containing the related objects (e.g., "<Inventory: hj6h5n>")
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

    return Response()


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_supplier_by_id(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleSupplierSerializer(supplier)
    return Response(serializer.data)


# @api_view(['DELETE'])
# def delete_suppliers(request):
#     # Ensure the request body contains a list of IDs
#     if not isinstance(request.data, list):
#         return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

#     # Retrieve and delete suppliers in a batch
#     try:
#         suppliers = Supplier.objects.filter(id__in=request.data)
#         if not suppliers.exists():
#             return Response({"detail": "None of the suppliers found."}, status=status.HTTP_404_NOT_FOUND)
#         count, _ = suppliers.delete()
#         return Response({"detail": f"{count} suppliers deleted successfully."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_suppliers(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        suppliers = Supplier.objects.filter(id__in=request.data)
        if not suppliers.exists():
            return Response({"detail": "None of the suppliers found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the suppliers
        try:
            count, _ = suppliers.delete()
            return Response({"detail": f"{count} suppliers deleted successfully."}, status=status.HTTP_200_OK)
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