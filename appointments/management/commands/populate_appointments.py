from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from appointments.models import Appointment, Bill
from pet_registration.models import Pet
from registration_login.models import Profile

class Command(BaseCommand):
    help = 'Populates the database with sample appointments'

    def handle(self, *args, **kwargs):
        # Get all pets and profiles
        pets = Pet.objects.all()
        if not pets.exists():
            self.stdout.write(self.style.ERROR('No pets found in the database. Please add some pets first.'))
            return

        # Sample data
        service_types = [choice[0] for choice in Appointment.SERVICE_CHOICES]
        statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
        
        # Create appointments for the next 30 days
        start_date = timezone.now().date()
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            # Create 2-4 appointments per day
            num_appointments = random.randint(2, 4)
            for _ in range(num_appointments):
                # Random time between 9 AM and 5 PM
                hour = random.randint(9, 16)
                minute = random.choice([0, 15, 30, 45])
                time = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
                
                # Get random pet and its owner
                pet = random.choice(pets)
                
                # Create appointment
                appointment = Appointment.objects.create(
                    pet=pet,
                    owner=pet.owner,
                    service_type=random.choice(service_types),
                    date=current_date,
                    time=time,
                    reason=f"Regular {random.choice(['checkup', 'maintenance', 'treatment'])}",
                    status=random.choice(statuses),
                    notes="Sample appointment note"
                )
                
                # Create corresponding bill
                amount = random.uniform(50.0, 500.0)
                Bill.objects.create(
                    appointment=appointment,
                    amount=round(amount, 2),
                    status=random.choice([choice[0] for choice in Bill.STATUS_CHOICES]),
                    due_date=current_date + timedelta(days=7)
                )
                
        self.stdout.write(self.style.SUCCESS('Successfully populated appointments'))
