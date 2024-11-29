from django.utils import timezone
from rest_framework import serializers
from app.features.supplier.models import Supplier
import re


class GetSingleSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'contact_name',
            'contact_phone',
            'operator_id',
            'location_id',
        ]


class SupplierGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    location = serializers.SerializerMethodField('get_location_name')

    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'contact_name',
            'contact_phone',
            'operator',
            'location',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_location_name(obj):
        return obj.location and obj.location.name


class SupplierCreateUpdateSerializer(serializers.ModelSerializer):
    # operator_id = serializers.CharField(max_length=10)
    location_id = serializers.CharField(max_length=10)

    class Meta:
        model = Supplier
        fields = [
            'name',
            'phone',
            'email',
            'contact_name',
            'contact_phone',
            # 'operator_id',
            'location_id',
        ]

    def validate_phone(self, value):
        """
        Validate the main phone number field.
        """
        phone_regex = re.compile(r"^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$")
        if not phone_regex.match(value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_contact_phone(self, value):
        """
        Validate the contact phone field only if it is provided.
        """
        if value:  # Check if the field is not empty
            phone_regex = re.compile(r"^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$")
            if not phone_regex.match(value):
                raise serializers.ValidationError("Enter a valid contact phone number.")
        return value