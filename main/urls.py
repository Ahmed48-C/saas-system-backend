"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
# )
from app.features.userprofile.token_helper import CustomTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.features.operator.urls')),
    path('api/', include('app.features.location.urls')),
    path('api/', include('app.features.userprofile.urls')),
    path('api/', include('app.features.supplier.urls')),
    path('api/', include('app.features.product.urls')),
    path('api/', include('app.features.store.urls')),
    path('api/', include('app.features.inventory.urls')),
    path('api/', include('app.features.reminder.urls')),
    path('api/', include('app.features.customer.urls')),
    path('api/', include('app.features.purchase_order.urls')),
    path('api/', include('app.features.balance.urls')),
    path('api/', include('app.features.balance_log.urls')),
    path('api/', include('app.features.transfer.urls')),

    # Token api using 'POST' request
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]

from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

from django.shortcuts import redirect

def redirect_to_ui(request):
    return redirect('/ui/dashboard')

# only for production or testing serving react from within django from local
urlpatterns += [
    re_path('ui\/.*',TemplateView.as_view(template_name='index.html')),

    path('', TemplateView.as_view(template_name='index.html')),  # Serve React app

    path('', redirect_to_ui),
    path('/', redirect_to_ui),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

