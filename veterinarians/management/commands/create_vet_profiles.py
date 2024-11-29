from django.core.management.base import BaseCommand
from registration_login.models import Profile
from veterinarians.models import VeterinarianProfile
from decimal import Decimal

class Command(BaseCommand):
    help = 'Creates VeterinarianProfile for existing VET users'

    def handle(self, *args, **kwargs):
        vet_profiles = Profile.objects.filter(role='VET')
        created_count = 0

        for profile in vet_profiles:
            vet_profile, created = VeterinarianProfile.objects.get_or_create(
                profile=profile,
                defaults={
                    'specialization': "General Veterinary Medicine",
                    'license_number': f"TEMP-{profile.user.username}",
                    'years_of_experience': 0,
                    'bio': f"Dr. {profile.first_name} {profile.last_name} is a veterinarian at PetVet.",
                    'available_days': "Monday,Tuesday,Wednesday,Thursday,Friday",
                    'consultation_fee': Decimal('50.00')
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} veterinarian profiles'
            )
        )
