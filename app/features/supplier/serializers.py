from django.utils import timezone
from rest_framework import serializers
from app.features.supplier.models import Supplier



class GetSingleSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'phone',
            'email',
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
    operator_id = serializers.CharField(max_length=10)
    location_id = serializers.CharField(max_length=10)

    class Meta:
        model = Supplier
        fields = [
            'name',
            'phone',
            'email',
            'operator_id',
            'location_id',
        ]