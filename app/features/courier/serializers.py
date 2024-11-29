from django.utils import timezone
from rest_framework import serializers
from app.features.courier.models import Courier
import re


class GetSingleCourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = [
            'id',
            'name',
            'phone',
            'vehicle_type',
            'is_available',
            'default_delivery_cost',
        ]


class CourierGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['id', 'name', 'phone', 'vehicle_type', 'is_available', 'default_delivery_cost']


class CourierCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Courier
        fields = [
            'name',
            'phone',
            'vehicle_type',
            'is_available',
            'default_delivery_cost',
        ]

    def validate_phone(self, value):
        """
        Validate the phone number field.
        """
        phone_regex = re.compile(r"^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$")
        if not phone_regex.match(value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value