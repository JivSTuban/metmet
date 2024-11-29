from django.contrib import admin
from .models import VeterinarianProfile, MedicalRecord, BillingRecord, Prescription

# Register your models here.

@admin.register(VeterinarianProfile)
class VeterinarianProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'specialization', 'license_number', 'years_of_experience')
    search_fields = ('profile__first_name', 'profile__last_name', 'license_number', 'specialization')
    list_filter = ('specialization',)
    list_per_page = 20
    ordering = ('profile__first_name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile__user')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'veterinarian', 'date', 'diagnosis', 'next_visit_date')
    list_filter = ('date', 'veterinarian')
    search_fields = ('pet__pet_name', 'diagnosis', 'veterinarian__profile__user__username')
    list_per_page = 20
    ordering = ('-date',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pet', 'veterinarian__profile__user')

@admin.register(BillingRecord)
class BillingRecordAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'amount', 'status', 'due_date', 'payment_date')
    list_filter = ('status', 'due_date')
    search_fields = ('medical_record__pet__pet_name', 'invoice_number')
    list_per_page = 20
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('medical_record__pet')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'medication_name', 'dosage', 'frequency', 'duration')
    list_filter = ('prescribed_date', 'medication_name')
    search_fields = ('medical_record__pet__pet_name', 'medication_name')
    list_per_page = 20
    ordering = ('-prescribed_date',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('medical_record__pet')
