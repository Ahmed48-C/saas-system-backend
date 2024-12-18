from rest_framework import serializers
from django.contrib.auth.models import User
from django.middleware import csrf
from app.features.userprofile.models import UserProfile
from app.features.permission_role.serializers import PermissionRoleSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenVerifyView,
    TokenRefreshView
)
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenVerifySerializer,
    TokenRefreshSerializer
)

import logging

logger = logging.getLogger(__name__)


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
        # data['refresh'] = str(refresh)

        # Add extra responses here
        data['user_profile'] = jwt_response_payload_handler(
            token=str(refresh.access_token),
            user=self.user
        )

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)

    #     try:
    #         serializer.is_valid(raise_exception=True)
    #     except TokenError as e:
    #         raise InvalidToken(e.args[0])

    #     data = serializer.validated_data

    #     response = Response(data, status=status.HTTP_200_OK)

    #     # Set the refresh token in a secure HttpOnly cookie
    #     refresh_token = data.get('refresh')
    #     # print(refresh_token)

    #     # csrf.get_token(request)
    #     # response.data = {"Success" : "Login successfully","data":data}
    #     # return response
    #     if refresh_token:
    #         response.set_cookie(
    #             key=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE'],
    #             value=refresh_token,
    #             expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
    #             secure=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_SECURE'],
    #             httponly=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_HTTP_ONLY'],
    #             samesite=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_SAMESITE']
    #         )

    #     # Optionally, set the CSRF token
    #     csrf_token = csrf.get_token(request)
    #     response['X-CSRFToken'] = csrf_token

    #     return response


class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        try:
            # Get the user from the token
            token = AccessToken(attrs['token'])
            user_id = token['user_id']
            self.user = User.objects.get(id=user_id)
            
            # Now we can use self.user like in CustomTokenObtainPairSerializer
            data['user_profile'] = jwt_response_payload_handler(
                token=attrs['token'],
                user=self.user
            )
            data['valid'] = True
        except (TokenError, User.DoesNotExist):
            return {'valid': False}

        return data


class CustomTokenVerifyView(TokenVerifyView):
    serializer_class = CustomTokenVerifySerializer


class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        print("Cookies received:", request.COOKIES)  # Debug line
        refresh_token = request.COOKIES.get('refresh_token')
        print("refresh_token:", refresh_token)  # Debug line
        
        if not refresh_token:
            return Response(
                {"error": "No refresh token cookie found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            # Get user for user_profile data
            user = User.objects.get(id=refresh['user_id'])
            user_profile_data = jwt_response_payload_handler(
                token=access_token,
                user=user
            )
            
            return Response({
                'access': access_token,
                'user_profile': user_profile_data
            })
            
        except TokenError as e:
            print("Token Error:", str(e))  # Debug line
            return Response(
                {"error": "Invalid refresh token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print("Unexpected error:", str(e))  # Debug line
            return Response(
                {"error": "Token refresh failed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# from rest_framework_simplejwt.tokens import RefreshToken
# from django.middleware import csrf
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.contrib.auth import authenticate
# from django.conf import settings
# from rest_framework import status

# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     access_token = str(refresh.access_token)
#     refresh_token = str(refresh)
    
#     user_profile = UserProfile.objects.prefetch_related("permission_role__function_rules").get(user=user)
#     user_serializer = UserProfileSerializer(user_profile)
#     rules = UserProfile.objects.fetch_rules(user_profile)
#     user_serializer.data["permission_role"]["function_rules"] = rules["function_rules"]
    
#     return {
#         'refresh': refresh_token,
#         'access': access_token,
#         'user_profile': user_serializer.data
#     }

# class LoginView(APIView):
#     def post(self, request, format=None):
#         data = request.data
#         response = Response()
#         username = data.get('username', None)
#         password = data.get('password', None)
#         user = authenticate(username=username, password=password)

#         if user is not None:
#             if user.is_active:
#                 token_data = get_tokens_for_user(user)
#                 response.set_cookie(
#                     key=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE'],
#                     value=token_data["refresh"],
#                     expires=24 * 60 * 60,
#                     secure=False,
#                     httponly=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_HTTP_ONLY'],
#                     samesite='None'
#                 )
#                 # response.set_cookie(
#                 #     key='refresh_token',
#                 #     value=str(token_data["refresh"]),
#                 #     expires=24 * 60 * 60,
#                 #     secure=False,
#                 #     httponly=True,
#                 #     samesite='None'
#                 # )
#                 # csrf.get_token(request)
#                 response.data = {
#                     # "Success": "Login successfully",
#                     # "data": {
#                         "refresh": token_data["refresh"],
#                         "access": token_data["access"],
#                         "user_profile": token_data["user_profile"]
#                     # }
#                 }
#                 return response
#             else:
#                 return Response(
#                     {"No active": "This account is not active!!"}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#         else:
#             return Response(
#                 {"Invalid": "Invalid username or password!!"}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )
