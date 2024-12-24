from django.utils import timezone
from rest_framework import serializers
from app.features.task.models import Task, TaskStatus


class GetSingleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'created_at', 'completed_at']


class TaskGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'created_at', 'completed_at']


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'status',
            'priority'
        ]

    def validate(self, data):
        # Get the instance if this is an update operation
        instance = self.instance
        
        if instance:
            if instance.status == TaskStatus.COMPLETED:
                raise serializers.ValidationError("Completed tasks cannot be edited.")
            elif instance.status == TaskStatus.CANCELLED:
                raise serializers.ValidationError("Cancelled tasks cannot be edited.")
        
        return data

    def create(self, validated_data):
        # Set completed_at if status is completed
        if validated_data.get('status') == TaskStatus.COMPLETED:
            validated_data['completed_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle completed_at field based on status change
        new_status = validated_data.get('status')
        if new_status == TaskStatus.COMPLETED:
            validated_data['completed_at'] = timezone.now()
        elif instance.status == TaskStatus.COMPLETED and new_status != TaskStatus.COMPLETED:
            validated_data['completed_at'] = None
            
        return super().update(instance, validated_data)
