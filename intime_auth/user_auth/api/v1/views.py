from collections import OrderedDict

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from user_auth import user_service
from user_auth.models import User
from intime_auth.user_auth import token_service
from user_auth.schemas import EditProfile, UserLogin, UserRegistration
from .serializers import (UserLoginSerializer, UserProfileViewSerializer,
                          UserRegistrationSerializer, UserProfileEditSerializer)


@api_view(['POST'])
def register(request: Request) -> Response:
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
def login(request: Request) -> Response:
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


@api_view(['POST'])
def logout(request: Request) -> Response:
    token = request.headers.get('Authorization')
    if token:
        token_service.add_invalid_token_to_cache(token)
        return Response(
            {'success': 'You have successfully logged out.'},
            status=status.HTTP_200_OK
        )


@api_view(['GET', 'PATCH', 'DELETE'])
def profile(request: Request, pk: int) -> Response:
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response(
            {'error': 'User with the given id doesn\'t exist.'},
            status=status.HTTP_404_NOT_FOUND
        )
    token = request.headers.get('Authorization')
    if not token:
        return Response(
            {'error': 'Authorization token not provided.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    if token_service.check_profile_view_permission(token, user.email):
        if token_service.check_token_not_used_for_logout(token):
            if token_service.check_token_signature_valid(token):
                if request.method == 'GET':
                    serializer = UserProfileViewSerializer(user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                if request.method == 'PATCH':
                    serializer = UserProfileEditSerializer(data=request.data, partial=True)
                    if serializer.is_valid():
                        profile_serialized: OrderedDict = serializer.validated_data
                        profile = EditProfile(
                            first_name=profile_serialized.get('first_name'),
                            last_name=profile_serialized.get('last_name'),
                            phone_number=profile_serialized.get('phone_number'),
                        )
                        result = user_service.edit_user_profile(user, profile)
                        success = result.get('success')
                        if success:
                            return Response(
                                {'success': success}, status=status.HTTP_200_OK
                            )
                if request.method == 'DELETE':
                    user.delete()
                    token_service.add_invalid_token_to_cache(token)
                    return Response(
                                {'success': 'You have deleted you profile.'},
                                status=status.HTTP_200_OK
                            )
        return Response(
            {'error': 'Expired or invalid authorization token. Please log in.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    return Response(
        {'error': 'You\'re not allowed to view or change profiles of other users.'},
        status=status.HTTP_403_FORBIDDEN
    )
