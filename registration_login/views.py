from django.shortcuts import render, redirect
from . forms import CreateUserForm, LoginForm
from django.contrib.auth.decorators import login_required

#Authentication models and functions
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

#Import Profile and UserDetails
from .models import Profile  # Import Profile model
from django.http import HttpResponse
from django.contrib.auth.models import User
from pet_registration.models import Pet

def homepage(request):
    return render(request, 'mainpages/homepage.html')

def landingpage(request):
    return render(request, 'mainpages/landingpage.html')

def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # Save the User instance
            user = form.save()

            # Create or get the Profile for the new user
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': form.cleaned_data.get('first_name'),
                    'last_name': form.cleaned_data.get('last_name'),
                    'role': form.cleaned_data.get('role'),
                }
            )
            
            if not created:
                # Update existing profile with form data
                profile.first_name = form.cleaned_data.get('first_name')
                profile.last_name = form.cleaned_data.get('last_name')
                profile.role = form.cleaned_data.get('role')
                profile.save()

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('registration_login:registration_success') 
        else:
            print(form.errors)

    context = {'form': form}
    return render(request, 'registration_login/register.html', context=context)

def my_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('homepage:index')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, 'registration_login/my_login.html', context=context)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('homepage:index')

def registration_success(request):
    return render(request, 'registration_login/registration_success.html')

def set_appointment(request):
    # Add your appointment logic here
    return render(request, 'appointments/set_appointment.html')

#def all_user(request):
#    return HttpResponse('Returning all user')

@login_required
def profile(request):
    if request.user.profile.role == 'VET':
        return redirect('veterinarians:vet_profile')
    
    # Ensure the User model has a related name for pets
    pets_count = Pet.objects.filter(owner=request.user).count()
    appointments_count = sum(pet.appointments.count() for pet in request.user.pets.all())
    pending_bills_count = 0  # This part needs careful review, as the original code seems complex
    
    context = {
        'pets_count': pets_count,
        'appointments_count': appointments_count,
        'pending_bills_count': pending_bills_count,
    }
    return render(request, 'registration_login/profile.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        # Update profile fields
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)
        profile.address = request.POST.get('address', profile.address)
        profile.contact_number = request.POST.get('contact_number', profile.contact_number)
        profile.preferred_payment = request.POST.get('preferred_payment', profile.preferred_payment)
        
        # Handle payment details based on preferred payment method
        if profile.preferred_payment == 'CARD':
            profile.card_number = request.POST.get('card_number', profile.card_number)
            profile.card_expiry = request.POST.get('card_expiry', profile.card_expiry)
        elif profile.preferred_payment in ['GCASH', 'MAYA']:
            profile.ewallet_number = request.POST.get('ewallet_number', profile.ewallet_number)
            
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            
        profile.save()
        
        # Update user email
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('registration_login:profile')
        
    context = {
        'profile': profile,
    }
    return render(request, 'registration_login/edit_profile.html', context)