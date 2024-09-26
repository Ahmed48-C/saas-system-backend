from django.utils import timezone
from rest_framework import serializers
from app.features.transfer.models import Transfer



class GetSingleTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = [
            'id',
            'amount',
            'note',
            'date',
            'operator_id',
            'balance_from_id',
            'balance_to_id',
        ]


class TransferGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    balance_from = serializers.SerializerMethodField('get_balance_from_name')
    balance_to = serializers.SerializerMethodField('get_balance_to_name')

    class Meta:
        model = Transfer
        fields = [
            'id',
            'amount',
            'note',
            'date',
            'operator',
            'balance_from',
            'balance_to',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_balance_from_name(obj):
        return obj.balance_from and obj.balance_from.name

    @staticmethod
    def get_balance_to_name(obj):
        return obj.balance_to and obj.balance_to.name


class TransferCreateUpdateSerializer(serializers.ModelSerializer):
    # operator_id = serializers.CharField(max_length=10)
    balance_from_id = serializers.CharField(max_length=10)
    balance_to_id = serializers.CharField(max_length=10)

    class Meta:
        model = Transfer
        fields = [
            'amount',
            'note',
            'date',
            # 'operator_id',
            'balance_from_id',
            'balance_to_id',
        ]