from django.utils import timezone
from rest_framework import serializers
from .models import TestModel, Location

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = ['id', 'name']


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