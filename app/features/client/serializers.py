from django.utils import timezone
from rest_framework import serializers
from app.features.client.models import Client


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