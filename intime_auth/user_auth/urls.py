from django.urls import path

from . import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile/<int:pk>/update/', views.edit_profile, name='edit_profile'),
    path('profile/<int:pk>/updated/', views.edit_profile_success, name='edit_profile_success'),
]

handler403 = 'user_auth.views.handle_forbidden'
handler404 = 'user_auth.views.handle_not_found'
