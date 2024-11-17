from django.utils import timezone
from rest_framework import serializers
from app.features.courier.models import Courier


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
        fields = ['id', 'name', 'phone', 'vehicle_type', 'is_available']


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