from django.contrib import admin
from .models import Pet, MedicalRecord, Vaccination, MedicalFile

# Register your models here.

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('pet_id', 'pet_name', 'owner', 'species', 'breed', 'birthday')
    search_fields = ('pet_name', 'pet_id', 'owner__user__username')
    list_filter = ('species', 'breed')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'date', 'diagnosis', 'treatment')
    search_fields = ('pet__pet_name', 'diagnosis')
    list_filter = ('date',)

@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ('pet', 'name', 'date', 'next_due', 'is_done')
    search_fields = ('pet__pet_name', 'name')
    list_filter = ('is_done', 'date')

@admin.register(MedicalFile)
class MedicalFileAdmin(admin.ModelAdmin):
    list_display = ('pet', 'name', 'date', 'file')
    search_fields = ('pet__pet_name', 'name')
    list_filter = ('date',)