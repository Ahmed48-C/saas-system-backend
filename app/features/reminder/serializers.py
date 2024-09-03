from django.utils import timezone
from rest_framework import serializers
from app.features.reminder.models import Reminder


class GetSingleReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'name', 'date', 'time', 'reached',]


class ReminderGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'name', 'date', 'time', 'reached',]


class ReminderCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reminder
        fields = [
            'name',
            'date',
            'time',
            'reached',
        ]