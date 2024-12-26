from django.utils import timezone
from rest_framework import serializers
from app.features.income.models import Income, IncomeCategory
from datetime import datetime
from django.utils.timezone import now
from app.features.balance_history.models import ActionType, BalanceHistory
from main.settings import IMAGE_PATH_CLOUDINARY


class GetSingleIncomeSerializer(serializers.ModelSerializer):
    attachment_file = serializers.SerializerMethodField('get_attachment_file')
    
    class Meta:
        model = Income
        fields = [
            'id',
            'amount',
            'type',
            'note',
            'date',
            'action',
            'attachment_file',
            'operator_id',
            'balance_id',
            'customer_id',
            'category_id',
        #     'amount',
        # 'type',
        # 'note',
        # 'date',
        # 'action',
        # 'operator',
        # 'balance',
        ]
    
    @staticmethod
    def get_attachment_file(obj):
        if obj.attachment:
            return IMAGE_PATH_CLOUDINARY + obj.attachment


class IncomeGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    balance = serializers.SerializerMethodField('get_balance_name')
    customer = serializers.SerializerMethodField('get_customer_name')
    category = serializers.SerializerMethodField('get_category_name')
    attachment_file = serializers.SerializerMethodField('get_attachment_file')

    class Meta:
        model = Income
        fields = [
            'id',
            'amount',
            'type',
            'note',
            'date',
            'action',
            'attachment_file',
            'operator',
            'balance',
            'customer',
            'category',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_balance_name(obj):
        return obj.balance and obj.balance.name

    @staticmethod
    def get_customer_name(obj):
        return obj.customer and obj.customer.name
    
    @staticmethod
    def get_category_name(obj):
        return obj.category and obj.category.name
    
    @staticmethod
    def get_attachment_file(obj):
        if obj.attachment:
            return IMAGE_PATH_CLOUDINARY + obj.attachment

class IncomeCategoryGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = ['id', 'name']

class IncomeCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = ['name']

class IncomeCreateUpdateSerializer(serializers.ModelSerializer):
    balance_id = serializers.CharField(max_length=10)
    customer_id = serializers.CharField(max_length=10)
    category_id = serializers.CharField(max_length=10)


    class Meta:
        model = Income
        fields = [
            'amount',
            'type',
            'note',
            'date',
            'action',
            'attachment',
            'balance_id',
            'customer_id',
            'category_id',
        ]

    def create(self, validated_data):
        # Create the Income instance
        income = super().create(validated_data)

        # Update the associated balance and income history if balance exists
        balance = income.balance
        if balance:
            previous_amount = balance.amount  # Store the current balance before changes
            balance.amount += income.amount  # Add the amount to the balance
            action_type = ActionType.DEPOSIT
            note = "Direct Deposit"

            balance.save()  # Save the updated balance

            # Create a BalanceHistory entry
            BalanceHistory.objects.create(
                amount=income.amount,
                previous_amount=previous_amount,
                current_amount=balance.amount,
                balance=balance,
                action=action_type,
                note=note,
                transfer_date=validated_data.get('date', now()),
            )

        return income
