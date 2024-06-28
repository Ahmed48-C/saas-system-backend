from django.utils import timezone
from rest_framework import serializers
from app.features.location.models import TestModel, Location

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = ['id', 'name']


class GetSingleLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'code',
            'note',
            'street',
            'city',
            'state',
            'postcode',
            'country',
        ]


class LocationGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'code']


class LocationCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = [
            'code',
            'name',
            'note',
            'street',
            'city',
            'state',
            'postcode',
            'country',
        ]