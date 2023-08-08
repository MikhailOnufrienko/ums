from django.urls import path

from . import views


app_name = 'auth_api'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile/<int:pk>/edit/', views.profile, name='edit_profile'),
    path('profile/<int:pk>/delete/', views.profile, name='delete_profile'),
]
