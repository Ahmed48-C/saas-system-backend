from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.expense.serializers import (
    ExpenseGetAllSerializer,
    ExpenseCreateUpdateSerializer,
    GetSingleExpenseSerializer,
    ExpenseCategoryGetAllSerializer,
    ExpenseCategoryCreateUpdateSerializer,
)

# Create your views here.

from app.features.expense.models import Expense, ExpenseCategory
from app.features.balance.models import Balance
from app.common.common import (
    add_timestamp_to_image_file,
    upload_image_by_thread,
)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_expense(request):
    records, actual_total_count = Expense.objects.get_all_by_limit(request)
    serializer = ExpenseGetAllSerializer(records, many=True)

    json_obj = Expense.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_expense(request):
    # Check if 'attachment' is in request data, and only process it if present
    if 'attachment' in request.data:
        attachment = add_timestamp_to_image_file(request.data['attachment'])

        # Verify that the image has a .png extension
        if not attachment.lower().endswith('.png'):
            return Response({"detail": "Image must be a PNG file."}, status=status.HTTP_400_BAD_REQUEST)

        request.data['attachment'] = attachment
        attachment_file = request.data.pop('attachment_file', None)  # Use pop with a default value

        if attachment_file:
            upload_image_by_thread(attachment_file, attachment)

    serializer = ExpenseCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    expense = serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if 'attachment' is in request data, and only process it if present
    if 'attachment' in request.data:
        attachment = add_timestamp_to_image_file(request.data['attachment'])

        # Verify that the image has a .png extension
        if not attachment.lower().endswith('.png'):
            return Response({"detail": "Image must be a PNG file."}, status=status.HTTP_400_BAD_REQUEST)

        request.data['attachment'] = attachment
        attachment_file = request.data.pop('attachment_file', None)  # Use pop with a default value

        if attachment_file:
            upload_image_by_thread(attachment_file, attachment)

    serializer = ExpenseCreateUpdateSerializer(expense, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
        expense.soft_delete()
    except Expense.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_expense_by_id(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleExpenseSerializer(expense)
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_expenses(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        expenses = Expense.objects.filter(id__in=request.data)
        if not expenses.exists():
            return Response({"detail": "None of the expenses found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected expenses
        for expense in expenses:
            expense.soft_delete()

        return Response({"detail": f"{expenses.count()} expenses deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_expense_category(request):
    records = ExpenseCategory.objects.all()
    serializer = ExpenseCategoryGetAllSerializer(records, many=True)

    json_obj = {
        'data': serializer.data
    }

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_expense_category(request):
    serializer = ExpenseCategoryCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_last_30_days_expenses(request):
    from datetime import datetime, timedelta
    from django.db.models import Sum
    
    # Calculate the date 30 days ago from today
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    # Get expenses for last 30 days
    expenses = Expense.objects.filter(date__gte=thirty_days_ago).order_by('-date')
    
    # Calculate total amount
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Prepare simplified expense data
    expense_list = []
    for expense in expenses:
        expense_list.append({
            'amount': expense.amount,
            'date': expense.date
        })
    
    return Response({
        'total_amount': total_amount,
        'expenses': expense_list
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_month_expenses(request):
    from datetime import datetime
    from django.db.models import Sum
    from django.utils import timezone
    
    # Get the current date
    today = timezone.now()
    # Get the first day of the current month
    first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get expenses for current month
    expenses = Expense.objects.filter(
        date__year=today.year,
        date__month=today.month
    ).order_by('-date')
    
    # Calculate total amount
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Prepare simplified expense data
    expense_list = []
    for expense in expenses:
        expense_list.append({
            'amount': expense.amount,
            'date': expense.date
        })
    
    return Response({
        'total_amount': total_amount,
        'expenses': expense_list
    })