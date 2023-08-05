from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseBadRequest, HttpRequest

from .models import User
from .schemas import UserRegistration


def create_user(request: HttpRequest) -> str:
    user = UserRegistration(
        username=request.POST.get('username'),
        password=request.POST.get('password'),
        email=request.POST.get('email')
    )
    if (check_login_not_exists(user.username)
        and check_email_not_exists(user.email)):
        success = save_user_to_database(user)
    return success


def check_login_not_exists(login: str) -> bool:
    try:
        user = User.objects.get(username=login)
        if user:
            raise HttpResponseBadRequest(
                content='A user with such login already exists.'
                        'Please provide another login.'
            )
    except User.DoesNotExist:
        return True


def check_email_not_exists(email: str) -> bool:
    try:
        email = User.objects.get(email=email)
        if email:
            raise HttpResponseBadRequest(
               content='A user with such email already exists.'
            )
    except User.DoesNotExist:
        return True


def save_user_to_database(user: UserRegistration) -> str:
    password_hash = make_password(user.password)
    new_user = User.objects.create(
        username=user.username,
        password_hash=password_hash,
        email=user.email
    )
    return 'You have successfully signed up. Please log in.'
