from django.utils import timezone
from rest_framework import serializers
from app.features.client_balance.models import ClientBalance
import re


class ClientBalanceGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    client = serializers.SerializerMethodField('get_client_name')

    class Meta:
        model = ClientBalance
        fields = [
            'id',
            'client',
            'amount',
            'last_updated_at',
            'operator',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_client_name(obj):
        return obj.client and obj.client.name