from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files import File
import os

# Profile model
class Profile(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('GCASH', 'GCash'),
        ('MAYA', 'Maya'),
    ]

    ROLE_CHOICES = [
        ('OWNER', 'Pet Owner'),
        ('VET', 'Veterinarian'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/profile.png')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=200, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    preferred_payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    card_number = models.CharField(max_length=16, blank=True, null=True)
    card_expiry = models.CharField(max_length=5, blank=True, null=True) 
    ewallet_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='OWNER')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
