from django.db import models
from django.contrib.auth.models import User
from registration_login.models import Profile
from pet_registration.models import Pet
from treatments.models import Treatment
from decimal import Decimal

class VeterinarianProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, default="General Veterinary Medicine")
    license_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    available_days = models.CharField(max_length=200, help_text="Comma-separated list of available days", default="Monday,Tuesday,Wednesday,Thursday,Friday")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))

    def __str__(self):
        return f"Dr. {self.profile.first_name} {self.profile.last_name}"

class MedicalRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    veterinarian = models.ForeignKey(VeterinarianProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField()
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Medical Record for {self.pet.name} - {self.date.date()}"

class BillingRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Bill #{self.invoice_number} - {self.medical_record.pet.name}"

class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    instructions = models.TextField()
    prescribed_date = models.DateField(auto_now_add=True)
    refills = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.medication_name} for {self.medical_record.pet.name}"