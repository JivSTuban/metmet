from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.homepage, name='index'),
    path('about/', views.about_us, name='about_us'),
]
