from django.db import models
from registration_login.models import Profile
from PIL import Image
import os
from datetime import date
from datetime import timedelta
from django.contrib.auth.models import User


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    pet_id = models.CharField(max_length=20, unique=True)
    pet_name = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    species = models.CharField(max_length=50)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')])
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    birthday = models.DateField()
    pet_description = models.TextField(blank=True, null=True)
    image_url = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    primary_veterinarian = models.ForeignKey('veterinarians.VeterinarianProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_pets'
    )

    def save(self, *args, **kwargs):
        if not self.pet_id:
            last_pet = Pet.objects.all().order_by('pk').last()
            if last_pet and last_pet.pet_id.startswith('PETID'):
                last_id_number = int(last_pet.pet_id.replace('PETID', ''))
                new_id_number = last_id_number + 1
            else:
                new_id_number = 1
            self.pet_id = f"PETID{new_id_number}"

        if self.image_url:
            img = Image.open(self.image_url)
            img_path = os.path.join('media/pet_images', f"{self.pet_id}.jpg")
            img_dir = os.path.dirname(img_path)
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            if img.mode in ("RGBA", "P"):  # Convert image to RGB mode if it has an alpha channel
                img = img.convert("RGB")
            img.save(img_path)
            self.image_url.name = os.path.join('pet_images', f"{self.pet_id}.jpg")

        super(Pet, self).save(*args, **kwargs)

    def age(self):
        today = date.today()
        years = today.year - self.birthday.year
        months = today.month - self.birthday.month
        days = today.day - self.birthday.day

        if days < 0:
            months -= 1
            days += (today.replace(day=1) - timedelta(days=1)).day

        if months < 0:
            years -= 1
            months += 12

        if years > 0:
            if months > 0:
                return f"{years} years, {months} months"
            else:
                return f"{years} years"
        elif months > 0:
            if days > 0:
                return f"{months} months, {days} days"
            else:
                return f"{months} months"
        else:
            return f"{days} days"

    def __str__(self):
        return f"{self.pet_name} ({self.breed})"
