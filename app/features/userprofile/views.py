from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from app.features.userprofile.models import UserProfile
from app.features.userprofile.serializers import (
    UserProfileCreateUpdateSerializer,
    UserProfileGetAllSerializer,
    UserProfileGetSingleSerializer,
)

@api_view(['GET'])
def get_all_userprofile(request):
    records, actual_total_count = UserProfile.objects.get_all_by_limit(request)
    serializer = UserProfileGetAllSerializer(records, many=True)

    json_obj = UserProfile.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)

@api_view(['POST'])
def create_userprofile(request):
    serializer = UserProfileCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_userprofile_by_id(request, userprofile_id):
    try:
        userprofile = UserProfile.objects.get(id=userprofile_id)
    except UserProfile.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileGetSingleSerializer(userprofile)
    return Response(serializer.data)


@api_view(['PUT'])
def update_userprofile(request, userprofile_id):
    try:
        userprofile = UserProfile.objects.get(id=userprofile_id)
    except UserProfile.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileCreateUpdateSerializer(userprofile, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_userprofile(request, userprofile_id):
    try:
        user_profile = UserProfile.objects.get(id=userprofile_id)
    except UserProfile.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    user_profile.user.delete()  # Delete the associated user
    return Response()
