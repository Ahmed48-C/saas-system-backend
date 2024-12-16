from django.shortcuts import render

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.reminder.serializers import (
    ReminderGetAllSerializer,
    ReminderCreateUpdateSerializer,
    GetSingleReminderSerializer,
)

# Create your views here.

from app.features.reminder.models import Reminder

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_reminder(request):
    records, actual_total_count = Reminder.objects.get_all_by_limit(request) #Reminder.objects.all()
    serializer = ReminderGetAllSerializer(records, many=True)

    json_obj = Reminder.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_reminder(request):
    serializer = ReminderCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_reminder(request, reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Reminder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    reminder.delete()
    return Response()

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_reminder(request, reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Reminder.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReminderCreateUpdateSerializer(reminder, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_reminder_by_id(request, reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Reminder.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleReminderSerializer(reminder)
    return Response(serializer.data)