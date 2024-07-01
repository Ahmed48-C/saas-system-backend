from rest_framework import serializers
from django.contrib.auth.models import User
from app.features.userprofile.models import UserProfile
from app.features.permission_role.serializers import PermissionRoleSerializer


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)



class UserProfileSerializer(serializers.ModelSerializer):
    permission_role = PermissionRoleSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'permission_role',
            'user_id',
            'location_id',
            'operator_id',
        ]


def jwt_response_payload_handler(token, user=None, request=None):
    user_profile = UserProfile.objects\
        .prefetch_related(
            "permission_role__function_rules",
        ).get(user=user.id)
    user_serializer = UserProfileSerializer(user_profile)
    rules = UserProfile.objects.fetch_rules(user_profile)

    user_serializer.data["permission_role"]["function_rules"] = rules["function_rules"]

    return user_serializer.data
    # return {
    #     'token': token,
    #     'user_profile': user_serializer.data,
    #     'email': user.email
    # }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['access'] = str(refresh.access_token)

        # Add extra responses here
        data['user_profile'] = jwt_response_payload_handler(
            token=str(refresh.access_token),
            user=self.user
        )

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer