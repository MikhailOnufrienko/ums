from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import user_service
from .models import User



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
        user_id = return_value['user_id']
        response = redirect('auth:profile', user_id)
        response.set_cookie(
            'token', token, httponly=True, max_age=settings.TOKEN_LIFE_IN_DAYS * 86400
        )
        return response
    return render(request, 'login.html', status=200)


@require_POST
def logout(request: HttpRequest) -> HttpResponse:
    success = user_service.logout_user(request)
    response = redirect('auth:login')
    response.content = success
    response.delete_cookie('token')
    return response


def profile(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(User, pk=pk)
    if user:
        result = user_service.get_user_profile(request, user)
        if result.get('auth_error'):
            user_id = result.get('user_id')
            return HttpResponseForbidden(
                render(request, '403.html', {'user_id': user_id})
            )
        if result.get('token_error'):
            return redirect('auth:login')
        context = result
        return render(request, 'profile.html', context, status=200)


def edit_profile(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        return_value: JsonResponse = user_service.edit_user_profile(request, user)
        return redirect('auth:edit_profile_success', pk)
    return render(request, 'edit_profile.html', status=200)


def edit_profile_success(request: HttpRequest, pk: int) -> HttpResponse:
    return render(
        request, 'edit_profile_success.html', {'user_id': pk}, content_type='text/html'
    )


def handle_forbidden(request, exception) -> HttpResponse:
    return render(request, '403.html', status=403)


def handle_not_found(request, exception) -> HttpResponse:
    return render(request, '404.html', status=404)
