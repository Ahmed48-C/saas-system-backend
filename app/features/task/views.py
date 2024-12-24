from django.shortcuts import render

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from app.features.task.serializers import (
    TaskGetAllSerializer,
    TaskCreateUpdateSerializer,
    GetSingleTaskSerializer,
)

# Create your views here.

from app.features.task.models import Task, TaskStatus, TaskPriority
from app.common.json_utils import JsonUtils


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_task(request):
    records, actual_total_count = Task.objects.get_all_by_limit(request) #Task.objects.all()
    serializer = TaskGetAllSerializer(records, many=True)

    json_obj = Task.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response()

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskCreateUpdateSerializer(task, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_task_by_id(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleTaskSerializer(task)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_task_status_choices(request):
    obj = JsonUtils.get_choices_as_list(TaskStatus.choices)
    return JsonResponse(obj, safe=False)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_task_priority_choices(request):
    obj = JsonUtils.get_choices_as_list(TaskPriority.choices)
    return JsonResponse(obj, safe=False)