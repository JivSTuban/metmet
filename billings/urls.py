from django.urls import path
from . import views

app_name = 'billings'

urlpatterns = [
    path('', views.billing_list, name='billing_list'),
    path('<int:bill_id>/', views.bill_details, name='bill_details'),
    path('<int:bill_id>/pay/', views.process_payment, name='process_payment'),
]
