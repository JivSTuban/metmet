from django.db import models
from pet_registration.models import Pet
from registration_login.models import Profile
from veterinarians.models import VeterinarianProfile

# Create your models here.
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    ]

    SERVICE_CHOICES = [
        ('CHECKUP', 'General Check-up'),
        ('VACCINATION', 'Vaccination'),
        ('SURGERY', 'Surgery'),
        ('GROOMING', 'Grooming'),
        ('DENTAL', 'Dental Care'),
        ('EMERGENCY', 'Emergency Care'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)  # Making owner nullable
    veterinarian = models.ForeignKey(VeterinarianProfile, on_delete=models.SET_NULL, null=True, related_name='appointments')
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='CHECKUP')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.pet.pet_name} - {self.service_type} ({self.date})"