from django.utils import timezone
from rest_framework import serializers
from app.features.expense.models import Expense, ExpenseCategory
from datetime import datetime
from django.utils.timezone import now
from app.features.balance_history.models import ActionType, BalanceHistory
from main.settings import IMAGE_PATH_CLOUDINARY


class GetSingleExpenseSerializer(serializers.ModelSerializer):
    attachment_file = serializers.SerializerMethodField('get_attachment_file')

    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'type',
            'note',
            'date',
            'action',
            'currency',
            'attachment_file',
            'operator_id',
            'balance_id',
            'supplier_id',
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


class ExpenseGetAllSerializer(serializers.ModelSerializer):
    operator = serializers.SerializerMethodField('get_operator_name')
    balance = serializers.SerializerMethodField('get_balance_name')
    supplier = serializers.SerializerMethodField('get_supplier_name')
    category = serializers.SerializerMethodField('get_category_name')
    attachment_file = serializers.SerializerMethodField('get_attachment_file')

    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'type',
            'note',
            'date',
            'action',
            'currency', 
            'attachment_file',
            'operator',
            'balance',
            'supplier',
            'category',
        ]

    @staticmethod
    def get_operator_name(obj):
        return obj.operator and obj.operator.name

    @staticmethod
    def get_balance_name(obj):
        return obj.balance and obj.balance.name

    @staticmethod
    def get_supplier_name(obj):
        return obj.supplier and obj.supplier.name
    
    @staticmethod
    def get_category_name(obj):
        return obj.category and obj.category.name
    
    @staticmethod
    def get_attachment_file(obj):
        if obj.attachment:
            return IMAGE_PATH_CLOUDINARY + obj.attachment


class ExpenseCategoryGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name']


class ExpenseCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['name']


class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    balance_id = serializers.CharField(max_length=10)
    supplier_id = serializers.CharField(max_length=10)
    category_id = serializers.CharField(max_length=10)

    class Meta:
        model = Expense
        fields = [
            'amount',
            'type',
            'note',
            'date',
            'action',
            'currency',
            'attachment',
            'balance_id',
            'supplier_id',
            'category_id',
        ]

    def create(self, validated_data):
        # Create the Expense instance
        expense = super().create(validated_data)

        # Update the associated balance and expense history if balance exists
        balance = expense.balance
        if balance:
            previous_amount = balance.amount  # Store the current balance before changes
            
            # Determine action type and note for BalanceHistory

            balance.amount -= expense.amount  # Subtract the amount from the balance
            action_type = ActionType.WITHDRAW
            note = "Direct Withdraw"

            balance.save()  # Save the updated balance

            # Create a BalanceHistory entry
            BalanceHistory.objects.create(
                amount=expense.amount,
                previous_amount=previous_amount,
                current_amount=balance.amount,
                balance=balance,
                action=action_type,
                note=note,
                transfer_date=validated_data.get('date', now()),
            )

        return expense
