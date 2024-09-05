from django.utils import timezone
from rest_framework import serializers
from app.features.balance_log.models import BalanceLog



class GetSingleBalanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceLog
        fields = [
            'id',
            'amount',
            'type',
            'note',
            'date',
            'action',
            'operator_id',
            'balance_id',
        #     'amount',
        # 'type',
        # 'note',
        # 'date',
        # 'action',
        # 'operator',
        # 'balance',
        ]


class BalanceLogGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    balance = serializers.SerializerMethodField('get_balance_name')

    class Meta:
        model = BalanceLog
        fields = [
            'id',
            'amount',
            'type',
            'note',
            'date',
            'action',
            'operator',
            'balance',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_balance_name(obj):
        return obj.balance and obj.balance.name


class BalanceLogCreateUpdateSerializer(serializers.ModelSerializer):
    # operator_id = serializers.CharField(max_length=10)
    balance_id = serializers.CharField(max_length=10)

    class Meta:
        model = BalanceLog
        fields = [
            'amount',
            'type',
            'note',
            'date',
            'action',
            # 'operator_id',
            'balance_id',
        ]