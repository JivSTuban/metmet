from django.urls import path
from . import views

app_name = 'registration_login'

urlpatterns = [
    path('login/', views.my_login, name='my_login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
