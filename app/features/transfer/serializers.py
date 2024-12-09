from django.utils import timezone
from rest_framework import serializers
from app.features.transfer.models import Transfer
from app.features.balance.models import Balance
from datetime import datetime
from django.utils.timezone import now
from app.features.balance_history.models import ActionType, BalanceHistory



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


# class TransferCreateUpdateSerializer(serializers.ModelSerializer):
#     # operator_id = serializers.CharField(max_length=10)
#     balance_from_id = serializers.CharField(max_length=10)
#     balance_to_id = serializers.CharField(max_length=10)

#     class Meta:
#         model = Transfer
#         fields = [
#             'amount',
#             'note',
#             'date',
#             # 'operator_id',
#             'balance_from_id',
#             'balance_to_id',
#         ]


class TransferCreateUpdateSerializer(serializers.ModelSerializer):
    balance_from_id = serializers.CharField(max_length=10)
    balance_to_id = serializers.CharField(max_length=10)

    class Meta:
        model = Transfer
        fields = [
            'amount',
            'note',
            'date',
            'balance_from_id',
            'balance_to_id',
        ]

    def validate(self, data):
        balance_from_id = data.get('balance_from_id')
        balance_to_id = data.get('balance_to_id')
        amount = data.get('amount')

        # Validation: amount must be greater than 0
        if amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than 0."})

        # Validation: balance_from and balance_to cannot be the same
        if balance_from_id == balance_to_id:
            raise serializers.ValidationError({"balance_from_id": "balance_from and balance_to cannot be the same."})

        # Ensure balances exist and check amounts
        try:
            balance_from = Balance.objects.get(id=balance_from_id)
        except Balance.DoesNotExist:
            raise serializers.ValidationError({"balance_from_id": "Balance from not found."})

        try:
            balance_to = Balance.objects.get(id=balance_to_id)
        except Balance.DoesNotExist:
            raise serializers.ValidationError({"balance_to_id": "Balance to not found."})

        # Validation: balance_from must have sufficient balance
        if balance_from.amount < amount:
            raise serializers.ValidationError({"amount": "Insufficient balance in balance_from."})

        # Add validated balance instances to the serializer context for use in create
        self.context['balance_from'] = balance_from
        self.context['balance_to'] = balance_to

        return data

    def create(self, validated_data):
        balance_from = self.context['balance_from']
        balance_to = self.context['balance_to']
        amount = validated_data['amount']

        # Store the previous amounts
        previous_amount_from = balance_from.amount
        previous_amount_to = balance_to.amount

        # Deduct from balance_from and add to balance_to
        balance_from.amount -= amount
        balance_to.amount += amount

        # Save the updated balances
        balance_from.save()
        balance_to.save()

        # Create BalanceHistory for balance_from
        BalanceHistory.objects.create(
            amount=amount,  # Negative to indicate deduction
            previous_amount=previous_amount_from,
            current_amount=balance_from.amount,
            balance=balance_from,
            action=ActionType.WITHDRAW,
            transfer_date=validated_data.get('date', now()),
            note="Transfer Out",
        )

        # Create BalanceHistory for balance_to
        BalanceHistory.objects.create(
            amount=amount,  # Positive to indicate addition
            previous_amount=previous_amount_to,
            current_amount=balance_to.amount,
            balance=balance_to,
            action=ActionType.DEPOSIT,
            transfer_date=validated_data.get('date', now()),
            note="Transfer In",
        )

        # Create and return the Transfer instance
        return Transfer.objects.create(
            balance_from=balance_from,
            balance_to=balance_to,
            amount=amount,
            note=validated_data.get('note'),
            date=validated_data.get('date')
        )

