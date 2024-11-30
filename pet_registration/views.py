from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from datetime import date, datetime
from .forms import PetRegistrationForm, PetUpdateForm, SPECIES_CHOICES
from registration_login.models import Profile
from .models import Pet
from appointments.models import Appointment
from treatments.models import Treatment

@login_required
def pet_registration(request):
    if request.method == 'POST':
        form = PetRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            
            # Find the most frequent veterinarian for this user's pets
            most_frequent_vet = Appointment.objects.filter(
                pet__owner=request.user
            ).values('veterinarian').annotate(
                vet_count=Count('veterinarian')
            ).order_by('-vet_count').first()
            
            if most_frequent_vet:
                pet.primary_veterinarian_id = most_frequent_vet['veterinarian']
            
            pet.save()
            return redirect('pet_registration:pet_registration_success', pet_id=pet.pet_id)
    else:
        form = PetRegistrationForm()
    return render(request, 'pet_registration/pet_registration.html', {'form': form})

@login_required
def update_pet(request, pet_id):
    pet = get_object_or_404(Pet, pet_id=pet_id)
    
    # Check if the user is the owner of the pet
    if pet.owner != request.user:
        messages.error(request, "You don't have permission to edit this pet's profile.")
        return redirect('pet_registration:pet_list_by_owner')

    if request.method == 'POST':
        form = PetRegistrationForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            updated_pet = form.save(commit=False)
            updated_pet.owner = pet.owner  # Ensure the owner remains unchanged
            updated_pet.save()
            messages.success(request, f"{pet.pet_name}'s profile has been updated successfully!")
            return redirect('pet_registration:pet_profile', pet_id=pet.pet_id)
    else:
        form = PetRegistrationForm(instance=pet)

    return render(request, 'pet_registration/pet_registration.html', {
        'form': form,
        'pet': pet,
        'is_update': True
    })

@login_required
def pet_list_by_owner(request):
    # Get all pets owned by this user
    pets = Pet.objects.filter(owner=request.user)
    # Get unique species
    species_list = [choice[0] for choice in SPECIES_CHOICES]  # Get just the values, not the display names
    return render(request, 'pet_registration/pet_list_by_owner.html', {
        'pets': pets,
        'species_list': species_list
    })

@login_required
def pet_profile(request, pet_id):
    pet = get_object_or_404(Pet, pet_id=pet_id)
    
    # Check if the user is the owner of the pet or a vet
    if request.user.profile.role != 'VET' and pet.owner != request.user:
        messages.error(request, "You don't have permission to view this pet's profile.")
        return redirect('pet_registration:pet_list_by_owner')
    
    # Get medical records
    medical_history = pet.medical_records.all()[:5]  # Get last 5 records
    
  
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        pet=pet,
        date__gte=date.today()
    ).order_by('date', 'time')[:5]
    
    # Get treatments
    treatments = Treatment.objects.filter(pet=pet).order_by('-scheduled_date')
    ongoing_treatments = treatments.filter(status='IN_PROGRESS')
    upcoming_treatments = treatments.filter(status='SCHEDULED')
    completed_treatments = treatments.filter(status='COMPLETED')[:5]  # Last 5 completed treatments
    
    
    # Get ongoing and upcoming appointments
    ongoing_appointments = Appointment.objects.filter(
        pet=pet, 
        status__in=['PENDING', 'APPROVED']
    )
    
    upcoming_appointments = Appointment.objects.filter(
        pet=pet, 
        date__gte=date.today()
    ).order_by('date')

    # Get completed and cancelled appointments
    completed_appointments = Appointment.objects.filter(
        pet=pet,
        status='COMPLETED'
    ).order_by('-date', '-time')
    
    cancelled_appointments = Appointment.objects.filter(
        pet=pet,
        status__in=['CANCELLED', 'REJECTED']
    ).order_by('-date', '-time')

    context = {
        'pet': pet,
        'medical_history': medical_history,
        'upcoming_appointments': upcoming_appointments,
        'ongoing_treatments': ongoing_treatments,
        'upcoming_treatments': upcoming_treatments,
        'completed_treatments': completed_treatments,
        'ongoing_appointments': ongoing_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'is_vet': request.user.profile.role == 'VET',
    }
    
    return render(request, 'pet_registration/pet_profile.html', context)

def pet_registration_success(request, pet_id):
    pet = get_object_or_404(Pet, pet_id=pet_id)
    return render(request, 'pet_registration/pet_registration_success.html', {'pet': pet})

@login_required
def delete_pet(request, pet_id):
    # Get the pet object or return 404
    pet = get_object_or_404(Pet, pet_id=pet_id)
    
    # Check if the logged-in user is the owner of the pet
    if pet.owner != request.user:
        messages.error(request, "You don't have permission to delete this pet.")
        return redirect('pet_registration:pet_list_by_owner')
    
    # Store pet name for success message
    pet_name = pet.pet_name
    
    # Delete the pet
    pet.delete()
    
    # Add success message
    messages.success(request, f'{pet_name} has been successfully removed.')
    
    return redirect('pet_registration:pet_list_by_owner')