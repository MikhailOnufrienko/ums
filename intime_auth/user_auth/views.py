from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from . import user_service



def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        return_value: dict = user_service.create_user(request)
        error = return_value.get('error_message', None)
        if error:
            return render(request, 'register.html', {'error': error}, status=400)
        return redirect('auth:login')
    return render(request, 'register.html', status=200)


def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        return_value: dict = user_service.login_user(request)
        error = return_value.get('error_message', None)
        if error:
            return render(request, 'login.html', {'error': error}, status=401)
        token = return_value['header']['Authorization']
        response = redirect('auth:profile')
        response.set_cookie(
            'token', token, httponly=True, max_age=settings.TOKEN_LIFE_IN_DAYS * 86400
        )
        return response
    return render(request, 'login.html', status=200)


def logout(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        success = user_service.logout_user(request)
        response = redirect('auth:login')
        response.content = success
        response.delete_cookie('token')
        return response


def profile(request: HttpRequest) -> HttpResponse:
    return render(request, 'profile.html', status=200)


