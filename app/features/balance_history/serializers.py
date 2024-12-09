from django.utils import timezone
from rest_framework import serializers
from app.features.balance_history.models import BalanceHistory


class BalanceHistoryGetAllSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField('get_balance_name')

    class Meta:
        model = BalanceHistory
        fields = [
            'id',
            'amount',
            'previous_amount',
            'current_amount',
            'balance',
            'action',
            'note',
            'transfer_date',
            'operator'
        ]

    @staticmethod
    def get_balance_name(obj):
        return obj.balance and obj.balance.name
