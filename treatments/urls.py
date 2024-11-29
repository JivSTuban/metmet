from django.urls import path
from . import views

app_name = 'treatments'

urlpatterns = [
    path('', views.treatment_list, name='treatment_list'),
    path('<int:treatment_id>/', views.treatment_detail, name='treatment_detail'),
    path('add/', views.add_treatment, name='add_treatment'),
    path('<int:treatment_id>/update/', views.update_treatment, name='update_treatment'),
    path('<int:treatment_id>/add-note/', views.add_treatment_note, name='add_treatment_note'),
    path('<int:treatment_id>/update-status/', views.update_treatment_status, name='update_treatment_status'),
    path('medications/', views.medication_list, name='medication_list'),
    path('procedures/', views.procedure_list, name='procedure_list'),
]
