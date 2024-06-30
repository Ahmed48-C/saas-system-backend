from django.utils import timezone
from rest_framework import serializers
from app.features.operator.models import Operator


class GetSingleOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = [
            'id',
            'name',
        ]


class OperatorGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id', 'name']


class OperatorCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Operator
        fields = [
            'name',
        ]