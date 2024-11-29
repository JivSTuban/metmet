from django.db.models.signals import post_save
from django.dispatch import receiver
from registration_login.models import Profile
from .models import VeterinarianProfile
from decimal import Decimal

@receiver(post_save, sender=Profile)
def create_or_update_vet_profile(sender, instance, created, **kwargs):
    """
    Signal to create or update VeterinarianProfile when a Profile is saved
    """
    if instance.role == 'VET':
        VeterinarianProfile.objects.get_or_create(
            profile=instance,
            defaults={
                'specialization': "General Veterinary Medicine",
                'license_number': f"TEMP-{instance.user.username}",
                'years_of_experience': 0,
                'bio': f"Dr. {instance.first_name} {instance.last_name} is a veterinarian at PetVet.",
                'available_days': "Monday,Tuesday,Wednesday,Thursday,Friday",
                'consultation_fee': Decimal('50.00')
            }
        )
