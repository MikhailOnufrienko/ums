from collections import OrderedDict

from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user_auth import user_service
from user_auth.models import User
from user_auth.schemas import UserLogin, UserRegistration
from .serializers import UserLoginSerializer, UserRegistrationSerializer


@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user_serialized: OrderedDict = serializer.validated_data
        user = UserRegistration(
            username=user_serialized.get('username'),
            password=user_serialized.get('password'),
            email=user_serialized.get('email')
        )
        result: dict = user_service.create_user(user)
        error = result.get('error_message', None)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        success = result.get('success_message', None)
        if success:
            return Response({'success': success}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user_serialized: OrderedDict = serializer.validated_data
        user = UserLogin(
            email=user_serialized.get('email'),
            password=user_serialized.get('password')
        )
        result: dict = user_service.login_user(user)
        error = result.get('error_message', None)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        success = result.get('success_message', None)
        if success:
            token = result['header']['Authorization']
            return Response(
                {'success': success},
                status=status.HTTP_200_OK,
                headers={'Authorization': token}
            )
