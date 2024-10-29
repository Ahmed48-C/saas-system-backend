from django.utils import timezone
from rest_framework import serializers
from app.features.store.models import Store

class GetSingleStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'code',
            'note',
            'street',
            'city',
            'state',
            'postcode',
            'country',
            'total_stock'
        ]


class StoreGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'code',
            'note',
            'street',
            'city',
            'state',
            'postcode',
            'country',
            'total_stock'
        ]


class StoreCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = [
            'code',
            'name',
            'note',
            'street',
            'city',
            'state',
            'postcode',
            'country',
            'total_stock'
        ]