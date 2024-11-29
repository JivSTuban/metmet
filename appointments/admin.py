from django.contrib import admin
from .models import Appointment

# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'owner', 'veterinarian', 'service_type', 'date', 'time', 'status')
    list_filter = ('status', 'service_type', 'date')
    search_fields = ('pet__pet_name', 'owner__user__username', 'veterinarian__profile__user__username')
    list_per_page = 20
    date_hierarchy = 'date'
    ordering = ('-date', '-time')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pet', 'owner', 'veterinarian')
