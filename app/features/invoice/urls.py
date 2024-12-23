from django.urls import path
from app.features.invoice.views import (
    get_all_invoice,
    create_invoice,
    update_invoice,
    delete_invoice,
    get_invoice_by_id,
    delete_invoices,
    get_invoice_payment_method_choices,
)

urlpatterns = [
    path('get/invoice/<invoice_id>/', get_invoice_by_id),
    path('get/invoices/', get_all_invoice),
    path('post/invoice/', create_invoice),
    path('put/invoice/<invoice_id>/', update_invoice),
    path('delete/invoice/<invoice_id>/', delete_invoice),
    path('delete/invoices/', delete_invoices),
    path('get/invoice_payment_methods/', get_invoice_payment_method_choices),
]
