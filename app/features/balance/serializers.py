from django.utils import timezone
from rest_framework import serializers
from app.features.balance.models import Balance

class GetSingleBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = [
            'id',
            'name',
            'amount',
            'operator_id'
        ]


class BalanceGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = [
            'id',
            'name',
            'amount',
            'operator'
        ]


class BalanceCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = [
            'name',
            'amount'
        ]