from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pet_registration.models import Pet
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Populates the database with sample pets'

    def handle(self, *args, **kwargs):
        # Sample data
        sample_pets = [
            {
                'name': 'Max',
                'species': 'Dog',
                'breed': 'Golden Retriever',
                'sex': 'Male',
                'weight': 30.5,
                'description': 'Friendly and energetic Golden Retriever who loves to play fetch.'
            },
            {
                'name': 'Luna',
                'species': 'Cat',
                'breed': 'Siamese',
                'sex': 'Female',
                'weight': 4.2,
                'description': 'Elegant Siamese cat with striking blue eyes.'
            },
            {
                'name': 'Charlie',
                'species': 'Dog',
                'breed': 'French Bulldog',
                'sex': 'Male',
                'weight': 12.3,
                'description': 'Playful Frenchie who loves belly rubs.'
            },
            {
                'name': 'Bella',
                'species': 'Cat',
                'breed': 'Persian',
                'sex': 'Female',
                'weight': 4.8,
                'description': 'Fluffy Persian cat who enjoys lounging in sunny spots.'
            },
            {
                'name': 'Rocky',
                'species': 'Dog',
                'breed': 'German Shepherd',
                'sex': 'Male',
                'weight': 35.7,
                'description': 'Loyal and intelligent German Shepherd.'
            },
            {
                'name': 'Coco',
                'species': 'Bird',
                'breed': 'African Grey Parrot',
                'sex': 'Female',
                'weight': 0.4,
                'description': 'Intelligent parrot who can mimic various sounds.'
            },
            {
                'name': 'Nemo',
                'species': 'Fish',
                'breed': 'Clownfish',
                'sex': 'Male',
                'weight': 0.1,
                'description': 'Vibrant clownfish swimming happily in the tank.'
            },
            {
                'name': 'Oreo',
                'species': 'Hamster',
                'breed': 'Syrian Hamster',
                'sex': 'Male',
                'weight': 0.15,
                'description': 'Active hamster who loves running on his wheel.'
            },
            {
                'name': 'Thumper',
                'species': 'Rabbit',
                'breed': 'Holland Lop',
                'sex': 'Male',
                'weight': 2.1,
                'description': 'Gentle rabbit with floppy ears.'
            },
            {
                'name': 'Rex',
                'species': 'Reptile',
                'breed': 'Bearded Dragon',
                'sex': 'Male',
                'weight': 0.5,
                'description': 'Calm and friendly bearded dragon.'
            }
        ]

        # Get all users
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create at least one user first.'))
            return

        # Delete existing pets (optional, comment out if you want to keep existing pets)
        Pet.objects.all().delete()

        # Create pets
        for pet_data in sample_pets:
            # Randomly select a user
            user = random.choice(users)
            
            # Generate a random birthday between 1 and 10 years ago
            days_old = random.randint(365, 3650)
            birthday = date.today() - timedelta(days=days_old)

            # Create the pet
            pet = Pet.objects.create(
                owner=user.profile,
                pet_name=pet_data['name'],
                breed=pet_data['breed'],
                species=pet_data['species'],
                sex=pet_data['sex'],
                weight=pet_data['weight'],
                birthday=birthday,
                pet_description=pet_data['description']
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created pet: {pet.pet_name}'))
