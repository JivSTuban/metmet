from django.db import models
from pet_registration.models import Pet
from registration_login.models import Profile
from django.utils import timezone

class Medication(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    dosage_instructions = models.TextField()
    side_effects = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Procedure(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField(help_text="Expected duration of the procedure")
    preparation_instructions = models.TextField()
    aftercare_instructions = models.TextField()
    risks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Treatment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    TREATMENT_TYPE_CHOICES = [
        ('CHECKUP', 'Regular Checkup'),
        ('MEDICATION', 'Medication'),
        ('PROCEDURE', 'Procedure'),
        ('EMERGENCY', 'Emergency Visit')
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='treatments')
    veterinarian = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'is_vet': True})
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPE_CHOICES, default='CHECKUP')
    medication = models.ForeignKey(Medication, on_delete=models.SET_NULL, null=True, blank=True)
    procedure = models.ForeignKey(Procedure, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Common fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Veterinary findings and recommendations
    symptoms = models.TextField(blank=True, help_text="Symptoms observed during visit")
    diagnosis = models.TextField(blank=True, help_text="Veterinary diagnosis")
    treatment_plan = models.TextField(blank=True, help_text="Detailed treatment plan")
    recommendations = models.TextField(blank=True, help_text="Additional recommendations for pet care")
    next_visit = models.DateTimeField(null=True, blank=True, help_text="Recommended date for next visit")
    
    # Medication specific fields
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    
    # Procedure specific fields
    procedure_notes = models.TextField(blank=True)
    complications = models.TextField(blank=True)
    
    # Progress tracking
    progress_notes = models.TextField(blank=True, help_text="Notes on treatment progress")
    owner_notes = models.TextField(blank=True, help_text="Notes from pet owner")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.medication and not self.procedure:
            raise ValidationError('Either medication or procedure must be specified')
        if self.medication and self.procedure:
            raise ValidationError('Cannot specify both medication and procedure')

    def save(self, *args, **kwargs):
        self.clean()
        if self.status == 'COMPLETED' and not self.completed_date:
            self.completed_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        treatment_type = self.medication.name if self.medication else self.procedure.name
        return f"{treatment_type} for {self.pet.pet_name}"

class TreatmentReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('UPCOMING', 'Upcoming Treatment'),
        ('MISSED', 'Missed Treatment'),
        ('FOLLOWUP', 'Follow-up Required')
    ]

    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    reminder_date = models.DateTimeField()
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_reminder_type_display()} for {self.treatment}"
