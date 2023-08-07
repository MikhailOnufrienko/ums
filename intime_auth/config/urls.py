from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user_auth.urls', namespace='auth')),
    path('api/v1/auth/', include('user_auth.api.v1.urls', namespace='auth_api')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
