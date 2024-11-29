from django.urls import path, re_path
from . import views

app_name = 'veterinarians'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/update/<int:appointment_id>/', views.update_appointment, name='update_appointment'),
    path('appointments/add-bill/<int:appointment_id>/', views.add_bill, name='add_bill'),
    
    # Medical Records URLs
    path('medical-records/', views.medical_records_list, name='medical_records_list'),
    path('medical-record/<int:record_id>/', views.medical_record_detail, name='medical_record_detail'),
    path('medical-records/add/<str:pet_id>/', views.add_medical_record, name='add_medical_record'),
    path('medical-records/pet/<str:pet_id>/', views.pet_medical_records, name='pet_medical_records'),
    path('medical-record/<int:record_id>/edit/', views.edit_medical_record, name='edit_medical_record'),
    
    # Billing and other URLs
    path('billing/', views.billing_management, name='billing_management'),
    path('billing/update/<int:bill_id>/', views.update_billing, name='update_billing'),
    path('profile/', views.vet_profile, name='vet_profile'),
]
