from django.urls import path
from app.features.product.views import (
    get_all_product,
    create_product,
    update_product,
    delete_product,
    get_product_by_id,
    delete_products,
)

urlpatterns = [
    path('get/product/<product_id>/', get_product_by_id),
    path('get/products/', get_all_product),
    path('post/product/', create_product),
    path('put/product/<product_id>/', update_product),
    path('delete/product/<product_id>/', delete_product),
    path('delete/products/', delete_products),
]