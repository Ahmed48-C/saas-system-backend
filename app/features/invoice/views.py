from django.shortcuts import render
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from rest_framework import status

# for JWT token and authentication control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.response import Response
from rest_framework import status
from app.features.invoice.serializers import (
    InvoiceGetAllSerializer,
    InvoiceCreateUpdateSerializer,
    GetSingleInvoiceSerializer,
)

# Create your views here.

from app.features.invoice.models import Invoice, InvoicePaymentMethod
from app.common.common import (
    add_timestamp_to_image_file,
    upload_image_by_thread,
)
from app.common.json_utils import JsonUtils

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_invoice(request):
    records, actual_total_count = Invoice.objects.get_all_by_limit(request) #Invoice.objects.all()
    serializer = InvoiceGetAllSerializer(records, many=True)

    json_obj = Invoice.objects.json_object(
        actual_total_count = actual_total_count,
        data = serializer.data
    )

    return Response(json_obj)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_invoice(request):
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

    serializer = InvoiceCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_invoice(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
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

    serializer = InvoiceCreateUpdateSerializer(invoice, data=request.data)
    serializer.is_valid(raise_exception=True)  # Raise exception on validation failure
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_invoice(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.soft_delete()
    except Invoice.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_invoice_by_id(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = GetSingleInvoiceSerializer(invoice)
    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_invoices(request):
    # Ensure the request body contains a list of IDs
    if not isinstance(request.data, list):
        return Response({"detail": "Invalid data format. Expected a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invoices = Invoice.objects.filter(id__in=request.data)
        if not invoices.exists():
            return Response({"detail": "None of the invoices found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete all selected invoices
        for invoice in invoices:
            invoice.soft_delete()

        return Response({"detail": f"{invoices.count()} invoices deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_invoice_payment_method_choices(request):
    obj = JsonUtils.get_choices_as_list(InvoicePaymentMethod.choices)
    return JsonResponse(obj, safe=False)