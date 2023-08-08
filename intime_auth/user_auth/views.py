from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from .schemas import EditProfile, UserLogin, UserRegistration

from . import user_service
from .models import User


@require_http_methods(['GET', 'POST'])
def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user = UserRegistration(
            username=request.POST.get('username'),
            password=request.POST.get('password'),
            email=request.POST.get('email')
        )
        return_value: dict = user_service.create_user(user)
        error = return_value.get('error_message', None)
        if error:
            return render(request, 'register.html', {'message': error}, status=400)
        success = return_value.get('success_message', None)
        if success:
            messages.success(request, success)
            return redirect('auth:login')
    return render(request, 'register.html', status=200)

@require_http_methods(['GET', 'POST'])
def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user = UserLogin(
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )
        return_value: dict = user_service.login_user(user)
        error = return_value.get('error_message', None)
        if error:
            messages.error(request, error)
            return render(request, 'login.html', status=401)
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


@require_GET
def profile(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(User, pk=pk)
    if user:
        result = user_service.get_user_profile(request, user)
        if result.get('auth_error'):
            failed_user_id = result.get('user_id')
            return HttpResponseForbidden(
                render(request, '403.html', {'user_id': failed_user_id})
            )
        token_error = result.get('token_error')
        if token_error:
            messages.error(request, token_error)
            return redirect('auth:login')
        context = result
        return render(request, 'profile.html', context, status=200)


@require_http_methods(['GET', 'POST'])
def edit_profile(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(User, pk=pk)
    if user:
        if request.method == 'POST':
            profile = EditProfile(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone_number=request.POST.get('phone_number')
            )
            result: dict = user_service.edit_user_profile(request, user, profile)
            if result.get('auth_error'):
                failed_user_id = result.get('user_id')
                return HttpResponseForbidden(
                    render(request, '403.html', {'user_id': failed_user_id})
                )
            token_error = result.get('token_error')
            if token_error:
                messages.error(request, token_error)
                return redirect('auth:login')
            return redirect('auth:edit_profile_success', pk)
    return render(request, 'edit_profile.html', status=200)


@require_POST
def delete_profile(request: HttpRequest, pk: int) -> HttpResponse:
    user = get_object_or_404(User, pk=pk)
    if user:
        user.delete()
        return redirect('auth:delete_profile_success')


def edit_profile_success(request: HttpRequest, pk: int) -> HttpResponse:
    return render(
        request, 'edit_profile_success.html', {'user_id': pk}, content_type='text/html'
    )


def delete_profile_success(request: HttpRequest) -> HttpResponse:
    return render(
        request, 'delete_profile_success.html', content_type='text/html'
    )


def handle_forbidden(request, exception) -> HttpResponse:
    return render(request, '403.html', status=403)


def handle_not_found(request, exception) -> HttpResponse:
    return render(request, '404.html', status=404)
