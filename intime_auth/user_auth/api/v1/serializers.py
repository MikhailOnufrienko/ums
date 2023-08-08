from rest_framework import serializers

from user_auth.models import User
from user_auth.schemas import UserRegistration


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField()
    email = serializers.EmailField()


class UserLoginSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()


class UserProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'full_name',
            'phone_number', 'joined_dt', 'last_modified_dt'
        ]


class UserProfileEditSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
