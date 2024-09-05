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
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_balance(request):
    records, actual_total_count = Balance.objects.get_all_by_limit(request) #Balance.objects.all()
    serializer = BalanceGetAllSerializer(records, many=True)

    json_obj = Balance.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_balance(request):
    serializer = BalanceCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
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
def delete_balance(request, balance_id):
    try:
        balance = Balance.objects.get(id=balance_id)
        balance.delete()
    except Balance.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except ProtectedError as e:
        # Extract the related instances causing the ProtectedError
        related_objects = e.protected_objects

        # Extracting the IDs of related objects
        related_ids = [obj.id for obj in related_objects]

        # Get the original error message
        original_message = str(e)

        # Find the part of the message containing the related objects (e.g., "<Inventory: hj6h5n>")
        start_idx = original_message.find("{")
        end_idx = original_message.find("}") + 1

        # Replace that part with the related IDs
        if start_idx != -1 and end_idx != -1:
            modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
        else:
            modified_message = original_message

        return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
    # except ProtectedError as e:
    #     # Return a more detailed error message
    #     return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()


@api_view(['GET'])
def get_balance_by_id(request, balance_id):
    try:
        balance = Balance.objects.get(id=balance_id)
    except Balance.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleBalanceSerializer(balance)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_balances(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        balances = Balance.objects.filter(id__in=request.data)
        if not balances.exists():
            return Response({"detail": "None of the balances found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the balances
        try:
            count, _ = balances.delete()
            return Response({"detail": f"{count} balances deleted successfully."}, status=status.HTTP_200_OK)
        except ProtectedError as e:
            # Extract the related instances causing the ProtectedError
            related_objects = e.protected_objects

            # Extracting the IDs of related objects
            related_ids = [obj.id for obj in related_objects]

            # Get the original error message
            original_message = str(e)

            # Find the part of the message containing the related objects (e.g., "<Product: hj6h5n>")
            start_idx = original_message.find("{")
            end_idx = original_message.find("}") + 1

            # Replace that part with the related IDs
            if start_idx != -1 and end_idx != -1:
                modified_message = original_message[:start_idx] + "{" + str(related_ids) + "}" + original_message[end_idx:]
            else:
                modified_message = original_message

            return JsonResponse({'error': modified_message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)