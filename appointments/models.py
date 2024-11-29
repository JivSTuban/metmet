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

class Bill(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('PARTIAL', 'Partially Paid'),
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='bill')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=Profile.PAYMENT_CHOICES, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.appointment.pet.pet_name} - {self.amount} ({self.status})"

    @property
    def remaining_amount(self):
        return self.amount - self.paid_amount