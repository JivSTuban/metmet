from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('new/', views.new_appointment, name='new_appointment'),
    path('create/', views.create_appointment, name='create_appointment'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('vet/appointments/', views.vet_appointment_list, name='vet_appointment_list'),
    path('vet/appointment/<int:pk>/approve/', views.approve_appointment, name='approve_appointment'),
    path('vet/appointment/<int:pk>/reject/', views.reject_appointment, name='reject_appointment'),
    path('vet/appointment/<int:pk>/complete/', views.complete_appointment, name='complete_appointment'),
]
