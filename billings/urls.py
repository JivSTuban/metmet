from django.urls import path
from . import views

app_name = 'billings'

urlpatterns = [
    path('', views.billing_list, name='billing_list'),
]
