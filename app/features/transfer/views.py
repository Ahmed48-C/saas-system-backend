from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.db import transaction

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.transfer.serializers import (
    TransferGetAllSerializer,
    TransferCreateUpdateSerializer,
    GetSingleTransferSerializer,
)

# Create your views here.

from app.features.transfer.models import Transfer
from app.features.balance.models import Balance


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_transfer(request):
    records, actual_total_count = Transfer.objects.get_all_by_limit(request)
    serializer = TransferGetAllSerializer(records, many=True)

    json_obj = Transfer.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@transaction.atomic  # Ensure that both balance changes are done atomically
def create_transfer(request):
    serializer = TransferCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Extract validated data
    balance_from_id = serializer.validated_data.get('balance_from_id')
    balance_to_id = serializer.validated_data.get('balance_to_id')
    amount = serializer.validated_data.get('amount')

    # Add validation to prevent transferring 0$
    if amount <= 0:
        return Response({"detail": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if balance_from and balance_to are the same
        if balance_from_id == balance_to_id:
            return Response({"detail": "balance_from and balance_to cannot be the same."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch balances for balance_from and balance_to
        balance_from = Balance.objects.get(id=balance_from_id)
        balance_to = Balance.objects.get(id=balance_to_id)

        # Ensure both balances exist and the transfer amount is valid
        if balance_from.amount < amount:
            return Response({"detail": "Insufficient balance in balance_from."}, status=status.HTTP_400_BAD_REQUEST)

        # Perform the transfer: Deduct from balance_from and add to balance_to
        balance_from.amount -= amount
        balance_to.amount += amount

        # Save both balances after modification
        balance_from.save()
        balance_to.save()

        # Save the Transfer entry
        transfer = serializer.save(balance_from=balance_from, balance_to=balance_to)

    except Balance.DoesNotExist:
        return Response({"detail": "Balance not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_transfer(request, transfer_id):
    try:
        transfer = Transfer.objects.get(id=transfer_id)
        transfer.delete()
    except Transfer.DoesNotExist:
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
def get_transfer_by_id(request, transfer_id):
    try:
        transfer = Transfer.objects.get(id=transfer_id)
    except Transfer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleTransferSerializer(transfer)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_transfers(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        transfers = Transfer.objects.filter(id__in=request.data)
        if not transfers.exists():
            return Response({"detail": "None of the transfers found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the transfers
        try:
            count, _ = transfers.delete()
            return Response({"detail": f"{count} transfers deleted successfully."}, status=status.HTTP_200_OK)
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