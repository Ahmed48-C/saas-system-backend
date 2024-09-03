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
from app.features.location.serializers import (
    TestSerializer,
    LocationGetAllSerializer,
    LocationCreateUpdateSerializer,
    GetSingleLocationSerializer,
)

# Create your views here.

from app.features.location.models import TestModel, Location

@api_view(['GET'])
def records_list(request):
    records = TestModel.objects.all()
    serializer = TestSerializer(records, many=True)
    return Response(serializer.data)



@api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_location(request):
    records, actual_total_count = Location.objects.get_all_by_limit(request) #Location.objects.all()
    serializer = LocationGetAllSerializer(records, many=True)

    json_obj = Location.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
def create_location(request):
    serializer = LocationCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
def update_location(request, location_id):
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocationCreateUpdateSerializer(location, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_location(request, location_id):
    try:
        location = Location.objects.get(id=location_id)
        location.delete()
    except Location.DoesNotExist:
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
def get_location_by_id(request, location_id):
    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleLocationSerializer(location)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_locations(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        locations = Location.objects.filter(id__in=request.data)
        if not locations.exists():
            return Response({"detail": "None of the locations found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to delete the locations
        try:
            count, _ = locations.delete()
            return Response({"detail": f"{count} locations deleted successfully."}, status=status.HTTP_200_OK)
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