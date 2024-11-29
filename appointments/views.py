from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Appointment
from pet_registration.models import Pet
from .forms import AppointmentForm
from datetime import timedelta

def create_appointment(request):
    """View for non-logged in users to create initial appointments"""
    if request.method == "POST":
        # Process the form data and create a temporary appointment
        service_type = request.POST.get('service_type', 'CHECKUP')
        date = request.POST.get('appointment_date')
        time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        owner_name = request.POST.get('owner_name')
        pet_name = request.POST.get('pet_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        # Store appointment details in session for later association
        request.session['pending_appointment'] = {
            'service_type': service_type,
            'date': date,
            'time': time,
            'reason': reason,
            'owner_name': owner_name,
            'pet_name': pet_name,
            'email': email,
            'phone_number': phone_number
        }
        
        messages.success(request, "Appointment request received! Our staff will contact you shortly to confirm.")
        return redirect('homepage:index')
    return redirect('homepage:index')

@login_required
def appointment_list(request):
    """View for logged-in users to see their appointments"""
    today = timezone.now().date()
    
    # Auto-complete past appointments that are still marked as scheduled
    Appointment.objects.filter(
        owner=request.user.profile,
        date__lt=today,
        status='PENDING'
    ).update(status='COMPLETED')

    # Get upcoming appointments (including today)
    upcoming_appointments = Appointment.objects.filter(
        owner=request.user.profile,
        date__gte=today,
        status__in=['PENDING', 'APPROVED']
    ).order_by('date', 'time')
    
    # Get past appointments
    past_appointments = Appointment.objects.filter(
        owner=request.user.profile,
        date__lt=today,
        status__in=['COMPLETED', 'CANCELLED']
    ).order_by('-date', '-time')[:5]  # Show last 5 appointments
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_detail(request, pk):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, pk=pk, owner=request.user.profile)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})

@login_required
def appointment_cancel(request, pk):
    """Cancel an appointment"""
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk, owner=request.user.profile)
        if appointment.status == 'PENDING':
            appointment.status = 'CANCELLED'
            appointment.save()
            messages.success(request, "Appointment cancelled successfully.")
        else:
            messages.error(request, "This appointment cannot be cancelled.")
        return redirect('appointments:appointment_list')
    return redirect('appointments:appointment_list')

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Check if user is authorized (owner of the appointment)
    if request.user.profile != appointment.owner:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('appointments:appointment_detail', pk=pk)
    
    # Check if appointment can be cancelled (only PENDING or APPROVED)
    if appointment.status not in ['PENDING', 'APPROVED']:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('appointments:appointment_detail', pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('appointments:appointment_list')
    
    return redirect('appointments:appointment_detail', pk=pk)

@login_required
def new_appointment(request):
    """Create new appointment for logged-in users"""
    initial_data = {}
    
    # Handle pre-selected pet from query parameters
    pet_id = request.GET.get('pet')
    if pet_id:
        try:
            pet = Pet.objects.get(pet_id=pet_id, owner=request.user.profile)
            initial_data['pet'] = pet
        except Pet.DoesNotExist:
            messages.error(request, "Invalid pet selected.")
    
    if request.method == "POST":
        form = AppointmentForm(request.user, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.owner = request.user.profile
            # The veterinarian is already saved through the form
            appointment.save()
            messages.success(request, "Appointment scheduled successfully!")
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm(request.user, initial=initial_data)
    
    context = {
        'form': form
    }
    return render(request, 'appointments/appointment_form.html', context)

@login_required
def vet_appointment_list(request):
    """View for vets to see and manage appointments"""
    if request.user.profile.role != 'VET':
        messages.error(request, "Access denied. Vet privileges required.")
        return redirect('homepage:index')
        
    pending_appointments = Appointment.objects.filter(
        status='PENDING'
    ).order_by('date', 'time')
    
    approved_appointments = Appointment.objects.filter(
        status='APPROVED'
    ).order_by('date', 'time')
    
    context = {
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
    }
    return render(request, 'appointments/vet_appointment_list.html', context)

@login_required
def approve_appointment(request, pk):
    """Approve an appointment"""
    if request.user.profile.role != 'VET':
        messages.error(request, "Access denied. Vet privileges required.")
        return redirect('homepage:index')
        
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.status = 'APPROVED'
        appointment.save()
        messages.success(request, "Appointment approved successfully.")
        return redirect('appointments:vet_appointment_list')
    return redirect('appointments:vet_appointment_list')

@login_required
def reject_appointment(request, pk):
    """Reject an appointment"""
    if request.user.profile.role != 'VET':
        messages.error(request, "Access denied. Vet privileges required.")
        return redirect('homepage:index')
        
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.status = 'REJECTED'
        appointment.save()
        messages.success(request, "Appointment rejected.")
        return redirect('appointments:vet_appointment_list')
    return redirect('appointments:vet_appointment_list')

@login_required
def complete_appointment(request, pk):
    """Mark appointment as completed"""
    if request.user.profile.role != 'VET':
        messages.error(request, "Access denied. Vet privileges required.")
        return redirect('homepage:index')
        
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)
        if appointment.status == 'APPROVED':
            appointment.status = 'COMPLETED'
            appointment.save()
            
            # Create a bill for the completed appointment
            service_prices = {
                'CHECKUP': 50.00,
                'VACCINATION': 75.00,
                'SURGERY': 500.00,
                'GROOMING': 40.00,
                'DENTAL': 150.00,
                'EMERGENCY': 200.00,
            }
            
            # Get the price based on service type, default to $50 if not found
            amount = service_prices.get(appointment.service_type, 50.00)
            
            # Create the bill with a due date 30 days from now
            Bill.objects.create(
                appointment=appointment,
                amount=amount,
                status='PENDING',
                due_date=timezone.now().date() + timedelta(days=30)
            )
            
            messages.success(request, "Appointment marked as completed and bill created.")
        else:
            messages.error(request, "Only approved appointments can be marked as completed.")
        return redirect('appointments:vet_appointment_list')
    return redirect('appointments:vet_appointment_list')

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is the owner of the appointment
    if request.user.profile != appointment.owner:
        messages.error(request, 'You do not have permission to edit this appointment.')
        return redirect('appointments:appointment_list')
    
    # Check if appointment can be edited (only PENDING appointments)
    if appointment.status != 'PENDING':
        messages.error(request, 'Only pending appointments can be edited.')
        return redirect('appointments:appointment_list')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        service_type = request.POST.get('service_type')
        reason = request.POST.get('reason')
        
        try:
            appointment.date = date
            appointment.time = time
            appointment.service_type = service_type
            appointment.reason = reason
            appointment.save()
            
            messages.success(request, 'Appointment updated successfully.')
            return redirect('appointments:appointment_list')
        except Exception as e:
            messages.error(request, f'Error updating appointment: {str(e)}')
    
    context = {
        'appointment': appointment,
        'service_choices': Appointment.SERVICE_CHOICES,
    }
    return render(request, 'appointments/edit_appointment.html', context)