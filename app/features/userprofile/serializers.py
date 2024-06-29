from rest_framework import serializers
from django.contrib.auth.models import User
from app.features.userprofile.models import UserProfile


class UserProfileGetSingleSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField('get_location')
    user = serializers.SerializerMethodField('get_username')
    email = serializers.SerializerMethodField('get_email')
    is_active = serializers.SerializerMethodField('get_is_active')

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'location',
            'user',
            'email',
            'is_active',
        ]

    @staticmethod
    def get_location(obj):
        return obj.location and obj.location.name

    @staticmethod
    def get_username(obj):
        return obj.user and obj.user.username

    @staticmethod
    def get_email(obj):
        return obj.user and obj.user.email

    @staticmethod
    def get_is_active(obj):
        return obj.user and obj.user.is_active


class UserProfileGetAllSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField('get_location')
    user = serializers.SerializerMethodField('get_username')

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'location',
            'user',
        ]

    @staticmethod
    def get_location(obj):
        return obj.location and obj.location.name

    @staticmethod
    def get_username(obj):
        return obj.user and obj.user.username


class UserProfileCreateUpdateSerializer(serializers.ModelSerializer):
    userprofile = serializers.PrimaryKeyRelatedField(read_only=True)  # Link to UserProfile
    username = serializers.CharField(
        max_length=200, required=False, allow_null=True, allow_blank=True)
    location_id = serializers.CharField(max_length=10, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'location_id', 'username', 'email', 'password', 'userprofile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        # Create a corresponding UserProfile
        UserProfile.objects.create(user=user, location_id=validated_data['location_id'])
        return user

    def update(self, instance, validated_data):
        if 'location_id' in validated_data:
            instance.location_id = validated_data['location_id']
            instance.save()
        instance.user.username = validated_data['username']
        instance.user.email = validated_data['email']
        instance.user.set_password(validated_data['password'])
        instance.user.save()
        return instance
