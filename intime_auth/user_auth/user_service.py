from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from jose import JWTError

from . import token_service
from .models import User
from .schemas import EditProfile, UserLogin, UserRegistration


def create_user(user: UserRegistration) -> dict:
    result = check_login_not_exists(user.username)
    if isinstance(result, str):
        error_message = result
        return {'error_message': error_message}
    result = check_email_not_exists(user.email)
    if isinstance(result, str):
        error_message = result
        return {'error_message': error_message}
    result = check_password_valid(user.password)
    if isinstance(result, str):
        error_message = result
        return {'error_message': error_message}
    success = save_user_to_database(user)
    return {'success_message': success}


def check_login_not_exists(login: str) -> bool | str:
    try:
        user = User.objects.get(username=login)
        if user:
            error_message =  ('A user with login %(login)s already exists. '
                            'Please provide another login.' %{'login': login})
            return error_message
    except User.DoesNotExist:
        return True


def check_email_not_exists(email: str) -> bool | str:
    try:
        user = User.objects.get(email=email)
        if user:
            error_message = ('A user with email %(email)s already exists. '
                            'Please provide another email.' %{'email': user.email})
            return error_message
    except User.DoesNotExist:
        return True
    

def check_password_valid(password: str) -> bool | str:
    try:
        validate_password(password)
    except ValidationError:
        return 'You password must be at least 8 characters.'


def save_user_to_database(user: UserRegistration) -> str:
    password_hash = make_password(user.password)
    User.objects.create(
        username=user.username,
        password_hash=password_hash,
        email=user.email
    )
    return 'You have successfully signed up. Please sign in.'


def login_user(user: UserLogin) -> dict:
    result = get_user_id_or_error(user.email, user.password)
    if isinstance(result, int):
        token = token_service.generate_tokens(result, user.email)
        success = "You have successfully logged in."
        header = {
            'Authorization': token
        }
        return {'success_message': success, 'header': header, 'user_id': result}
    error = result
    return {'error_message': error}
        

def get_user_id_or_error(email: str, password: str) -> int | str:
    try:
        user = User.objects.get(email=email)
        if user:
            user_id = user.id
            password_hash = user.password_hash
            if check_password(password, password_hash):
                return user_id
            raise User.DoesNotExist
    except User.DoesNotExist:
        error = 'You have entered the wrong login or password.<br>Please try again.'
        return error


def logout_user(request: HttpRequest) -> str:
        token = request.COOKIES.get('token')
        token_service.add_invalid_token_to_cache(token)
        return 'You have successfully logged out.'


def get_user_profile(request: HttpRequest, user: User) -> dict:
    result = check_token_OK_and_get_claims_or_return_error(request, user)
    token, email, user_id = (
        result.get('token'), result.get('email'), result.get('user_id')
    )
    if token and token != '':
        if token_service.check_profile_view_permission(token, email):
            if token_service.check_token_not_used_for_logout(token):
                if token_service.check_token_signature_valid(token):
                    success = {
                        'user_id': user_id,
                        'username': user.username,
                        'email': user.email,
                        'joined': user.joined_dt,
                        'last_modified': user.last_modified_dt,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number
                    }
                    return success
            return {
                'token_error': 'Invalid or expired authorization token. Please log in.'
            }
        return {
            'auth_error': 'You\'re not allowed to view profile of other users.',
            'user_id': user_id
        }
    return result
   

def edit_user_profile(request: HttpRequest, user: User, profile: EditProfile) -> dict:
    result = check_token_OK_and_get_claims_or_return_error(request, user)
    token, email, user_id = (
        result.get('token'), result.get('email'), result.get('user_id')
    )
    if token:
        if token_service.check_profile_view_permission(token, email):
            if token_service.check_token_not_used_for_logout(token):
                if token_service.check_token_signature_valid(token):
                    if profile.first_name and profile.first_name != '':
                        user.first_name = profile.first_name
                    if profile.last_name and profile.last_name != '':
                        user.last_name = profile.last_name
                    if profile.phone_number and profile.phone_number != '':
                        user.phone_number = profile.phone_number
                    user.save()
                    return {'success': 'Profile updated successfully.'}
            return {
                'token_error': 'Invalid or expired authorization token. Please log in.'
            }
        return {
            'auth_error': 'You\'re not allowed to view profile of other users.',
            'user_id': user_id
        }
    return result


def check_token_OK_and_get_claims_or_return_error(
        request: HttpRequest, user: User
) -> dict:
    try:
        token = request.COOKIES['token']
        email = user.email
        user_id = token_service.get_id_by_token(token)
        return {'token': token, 'email': email, 'user_id': user_id}
    except KeyError:
        return {'token_error': 'Authorization token not provided. Please log in.'}
    except JWTError:
        return {'token_error': 'Authorization token is invalid. Please log in.'}
