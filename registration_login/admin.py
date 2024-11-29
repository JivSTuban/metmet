from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'contact_number', 'role')
    search_fields = ('user__username', 'first_name', 'last_name', 'contact_number')
    list_filter = ('role', 'preferred_payment')
    list_per_page = 20
    ordering = ('user__username',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Customize the User admin to include Profile information
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
