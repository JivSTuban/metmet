from django.contrib import admin
from .models import Pet

# Register your models here.

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('pet_id', 'pet_name', 'owner', 'species', 'breed', 'birthday')
    search_fields = ('pet_name', 'pet_id', 'owner__username')
    list_filter = ('species', 'breed')
    list_per_page = 20
    ordering = ('pet_name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')
