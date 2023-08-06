from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpRequest

from .models import User
from .schemas import UserLogin, UserRegistration
from . import token_service


def create_user(request: HttpRequest) -> dict:
    user = UserRegistration(
        username=request.POST.get('username'),
        password=request.POST.get('password'),
        email=request.POST.get('email')
    )
    return_value = check_login_not_exists(user.username)
    if isinstance(return_value, str):
        error_message = return_value
        return {'error_message': error_message}
    return_value = check_email_not_exists(user.email)
    if isinstance(return_value, str):
        error_message = return_value
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
        email = User.objects.get(email=email)
        if email:
            error_message = ('A user with email %(email)s already exists. '
                            'Please provide another email.' %{'email': email})
            return error_message
    except User.DoesNotExist:
        return True


def save_user_to_database(user: UserRegistration) -> str:
    password_hash = make_password(user.password)
    User.objects.create(
        username=user.username,
        password_hash=password_hash,
        email=user.email
    )
    return 'You have successfully signed up. Please log in.'


def login_user(request: HttpRequest) -> dict:
    user = UserLogin(
        email=request.POST.get('email'),
        password=request.POST.get('password')
    )
    return_value =  check_credentials_correct(user.email, user.password)
    if isinstance(return_value, bool):
        token = token_service.generate_tokens(user.email)
        success = "You have successfully logged in."
        header = {
            'Authorization': token
        }
        return {'success_message': success, 'header': header}
    error = return_value
    return {'error_message': error}
        

def check_credentials_correct(email: str, password: str) -> bool | str:
    user = User.objects.get(email=email)
    if user:
        password_hash = user.password_hash
        if check_password(password, password_hash):
            return True
    error_message = 'You have entered incorrect login or password.'
    return error_message


def logout_user(request: HttpRequest) -> str:
        token = request.COOKIES.get('token')
        token_service.add_invalid_token_to_cache(token)
        return 'You have successfully logged out.'
