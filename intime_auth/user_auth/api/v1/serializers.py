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
