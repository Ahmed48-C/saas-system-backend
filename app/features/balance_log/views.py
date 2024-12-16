from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.balance_log.serializers import (
    BalanceLogGetAllSerializer,
    BalanceLogCreateUpdateSerializer,
    GetSingleBalanceLogSerializer,
)

# Create your views here.

from app.features.balance_log.models import BalanceLog
from app.features.balance.models import Balance


@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_balance_log(request):
    records, actual_total_count = BalanceLog.objects.get_all_by_limit(request)
    serializer = BalanceLogGetAllSerializer(records, many=True)

    json_obj = BalanceLog.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


# @api_view(['POST'])
# def create_balance_log(request):
#     serializer = BalanceLogCreateUpdateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data)

# @api_view(['POST'])
# def create_balance_log(request):
#     serializer = BalanceLogCreateUpdateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)

#     # Save the BalanceLog entry
#     balance_log = serializer.save()

#     # Check if the action is 'add' and update the Balance
#     if balance_log.action == 'Add' and balance_log.balance:
#         balance = balance_log.balance
#         balance.amount += balance_log.amount  # Add the amount to the current balance
#         balance.save()  # Save the updated balance
#     elif balance_log.action == 'Subtract' and balance_log.balance:
#         balance = balance_log.balance
#         balance.amount -= balance_log.amount  # Add the amount to the current balance
#         balance.save()  # Save the updated balance

#     return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_balance_log(request):
    serializer = BalanceLogCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    balance_log = serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_balance_log(request, balance_log_id):
    try:
        balance_log = BalanceLog.objects.get(id=balance_log_id)
    except BalanceLog.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BalanceLogCreateUpdateSerializer(balance_log, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_balance_log(request, balance_log_id):
    try:
        balance_log = BalanceLog.objects.get(id=balance_log_id)
        balance_log.delete()
    except BalanceLog.DoesNotExist:
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
def get_balance_log_by_id(request, balance_log_id):
    try:
        balance_log = BalanceLog.objects.get(id=balance_log_id)
    except BalanceLog.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleBalanceLogSerializer(balance_log)
    return Response(serializer.data)


# @api_view(['DELETE'])
# def delete_balance_logs(request):
#     # Ensure the request body contains a list of IDs
#     if not isinstance(request.data, list):
#         return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

#     # Retrieve and delete balance_logs in a batch
#     try:
#         balance_logs = BalanceLog.objects.filter(id__in=request.data)
#         if not balance_logs.exists():
#             return Response({"detail": "None of the balance_logs found."}, status=status.HTTP_404_NOT_FOUND)
#         count, _ = balance_logs.delete()
#         return Response({"detail": f"{count} balance_logs deleted successfully."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_balance_logs(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        balance_logs = BalanceLog.objects.filter(id__in=request.data)
        if not balance_logs.exists():
            return Response({"detail": "None of the balance_logs found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the balance_logs
        try:
            count, _ = balance_logs.delete()
            return Response({"detail": f"{count} balance_logs deleted successfully."}, status=status.HTTP_200_OK)
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