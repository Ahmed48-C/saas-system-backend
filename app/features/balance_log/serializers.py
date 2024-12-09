from django.utils import timezone
from rest_framework import serializers
from app.features.balance_log.models import BalanceLog
from datetime import datetime
from django.utils.timezone import now
from app.features.balance_history.models import ActionType, BalanceHistory


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


# class BalanceLogCreateUpdateSerializer(serializers.ModelSerializer):
#     # operator_id = serializers.CharField(max_length=10)
#     balance_id = serializers.CharField(max_length=10)

#     class Meta:
#         model = BalanceLog
#         fields = [
#             'amount',
#             'type',
#             'note',
#             'date',
#             'action',
#             # 'operator_id',
#             'balance_id',
#         ]



class BalanceLogCreateUpdateSerializer(serializers.ModelSerializer):
    balance_id = serializers.CharField(max_length=10)

    class Meta:
        model = BalanceLog
        fields = [
            'amount',
            'type',
            'note',
            'date',
            'action',
            'balance_id',
        ]

    def create(self, validated_data):
        # Create the BalanceLog instance
        balance_log = super().create(validated_data)

        # Update the associated balance and log history if balance exists
        balance = balance_log.balance
        if balance:
            previous_amount = balance.amount  # Store the current balance before changes
            
            # Determine action type and note for BalanceHistory
            if balance_log.action == 'Add':
                balance.amount += balance_log.amount  # Add the amount to the balance
                action_type = ActionType.DEPOSIT
                note = "Direct Deposit"
            elif balance_log.action == 'Subtract':
                balance.amount -= balance_log.amount  # Subtract the amount from the balance
                action_type = ActionType.WITHDRAW
                note = "Direct Withdraw"

            balance.save()  # Save the updated balance

            # Create a BalanceHistory entry
            BalanceHistory.objects.create(
                amount=balance_log.amount,
                previous_amount=previous_amount,
                current_amount=balance.amount,
                balance=balance,
                action=action_type,
                note=note,
                transfer_date=validated_data.get('date', now()),
            )

        return balance_log