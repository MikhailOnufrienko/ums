from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from . import user_service



def register(request: HttpRequest) -> HttpResponse:
    """User registration form."""
    if request.method == 'POST':
        success = user_service.create_user(request)
        messages.success(request, success)
        #return redirect('login')
        return HttpResponse(success)
    return render(request, 'register.html', status=200)
