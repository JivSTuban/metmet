from django.contrib import admin
from .models import Appointment, Bill

# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'owner', 'service_type', 'veterinarian', 'date', 'time', 'status')
    search_fields = ('pet__pet_name', 'owner__first_name', 'owner__last_name')
    list_filter = ('status', 'service_type', 'date')
    date_hierarchy = 'date'

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'amount', 'status', 'due_date', 'payment_method')
    list_filter = ('status', 'payment_method', 'due_date')
    search_fields = ('appointment__pet__pet_name', 'appointment__owner__first_name')
    date_hierarchy = 'due_date'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('appointment', 'amount')
        return ()
