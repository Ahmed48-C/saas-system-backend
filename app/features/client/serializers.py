from django.utils import timezone
from rest_framework import serializers
from app.features.client.models import Client
import re


class GetSingleClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id',
            'name',
            'phone',
            'share_percentage',
            'is_active',
        ]


class ClientGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'phone', 'share_percentage', 'is_active']


class ClientCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = [
            'name',
            'phone',
            'share_percentage',
            'is_active',
        ]
    
    def validate_phone(self, value):
        """
        Validate the phone number field.
        """
        phone_regex = re.compile(r"^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$")
        if not phone_regex.match(value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value