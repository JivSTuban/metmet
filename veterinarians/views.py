from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import VeterinarianProfile, MedicalRecord, BillingRecord, Prescription
from appointments.models import Appointment
from pet_registration.models import Pet
from treatments.models import Treatment, Medication, Procedure
import uuid
import random
import string

def is_veterinarian(user):
    return user.profile.role == 'VET'

@login_required
@user_passes_test(is_veterinarian)
def dashboard(request):
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    today = datetime.now().date()
    
    # Get today's appointments
    today_appointments = Appointment.objects.filter(
        veterinarian=vet_profile,
        date=today
    ).order_by('time')
    
    # Get pending appointments
    pending_appointments = Appointment.objects.filter(
        Q(veterinarian=vet_profile) & Q(status='PENDING')
    ).order_by('date', 'time')
    
    # Get recent medical records
    recent_records = MedicalRecord.objects.filter(
        veterinarian=vet_profile
    ).order_by('-date')[:5]
    
    # Get pending bills
    pending_bills = BillingRecord.objects.filter(
        medical_record__veterinarian=vet_profile,
        status='PENDING'
    ).order_by('due_date')
    
    context = {
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'recent_records': recent_records,
        'pending_bills': pending_bills,
    }
    return render(request, 'veterinarians/dashboard.html', context)

@login_required
@user_passes_test(is_veterinarian)
def appointment_list(request):
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    
    # Define the status order
    status_order = {
        'PENDING': 0,
        'APPROVED': 1,
        'COMPLETED': 2,
        'CANCELLED': 3,
        'REJECTED': 4
    }
    
    # Get all appointments
    appointments = Appointment.objects.select_related('pet', 'pet__owner').filter(
        veterinarian=vet_profile
    )
    
    # Sort appointments by status order, then by date and time
    appointments = sorted(appointments, key=lambda x: (status_order[x.status], x.date, x.time))
    
    # Debug print
    for appointment in appointments:
        print(f"Appointment ID: {appointment.id}")
        print(f"Pet: {appointment.pet}")
        if appointment.pet:
            print(f"Pet ID: {appointment.pet.pet_id}")
    
    return render(request, 'veterinarians/appointment_list.html', {'appointments': appointments})

@login_required
@user_passes_test(is_veterinarian)
def update_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    today = datetime.now().date()
    can_complete = appointment.date <= today
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        # Only allow completion if the appointment date is today or in the past
        if status == 'COMPLETED' and not can_complete:
            messages.error(request, 'Cannot mark future appointments as completed.')
            return render(request, 'veterinarians/update_appointment.html', {
                'appointment': appointment,
                'can_complete': can_complete
            })
            
        appointment.status = status
        appointment.notes = notes
        appointment.save()
        messages.success(request, 'Appointment updated successfully.')
        return redirect('veterinarians:appointment_list')
    
    return render(request, 'veterinarians/update_appointment.html', {
        'appointment': appointment,
        'can_complete': can_complete
    })

@login_required
@user_passes_test(is_veterinarian)
def medical_records_list(request):
    # Get the veterinarian profile for the current user
    try:
        vet_profile = VeterinarianProfile.objects.get(profile=request.user.profile)
    except VeterinarianProfile.DoesNotExist:
        messages.error(request, 'Veterinarian profile not found.')
        return redirect('veterinarians:dashboard')
    
    # Get pets with medical records for the current veterinarian
    pets_with_records = Pet.objects.filter(
        medical_records__veterinarian=vet_profile
    ).distinct()
    
    return render(request, 'veterinarians/medical_records_list.html', {
        'pets': pets_with_records
    })

@login_required
@user_passes_test(is_veterinarian)
def pet_medical_records(request, pet_id):
    # Remove 'PETID' prefix if present
    if pet_id.startswith('PETID'):
        pet_id = pet_id.replace('PETID', '')
    
    try:
        pet = get_object_or_404(Pet, pk=int(pet_id))
    except ValueError:
        messages.error(request, 'Invalid pet ID.')
        return redirect('veterinarians:medical_records_list')
    
    # Get the veterinarian profile for the current user
    try:
        vet_profile = VeterinarianProfile.objects.get(profile=request.user.profile)
    except VeterinarianProfile.DoesNotExist:
        messages.error(request, 'Veterinarian profile not found.')
        return redirect('veterinarians:dashboard')
    
    # Get medical records for the specific pet
    records = MedicalRecord.objects.filter(
        pet=pet, 
        veterinarian=vet_profile
    ).order_by('-date')
    
    context = {
        'pet': pet,
        'records': records
    }
    
    return render(request, 'veterinarians/pet_medical_records.html', context)

@login_required
@user_passes_test(is_veterinarian)
def add_medical_record(request, pet_id):
    # Remove 'PETID' prefix if present
    if pet_id.startswith('PETID'):
        pet_id = pet_id.replace('PETID', '')
    
    try:
        pet = get_object_or_404(Pet, pk=int(pet_id))
    except ValueError:
        messages.error(request, 'Invalid pet ID.')
        return redirect('veterinarians:medical_records_list')
    
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    
    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        treatment_description = request.POST.get('treatment', '').strip()
        treatment = None
        if treatment_description:
            # Create or get a medication for the treatment
            medication, created = Medication.objects.get_or_create(
                name=treatment_description,
                defaults={
                    'description': treatment_description,
                    'dosage_instructions': request.POST.get('dosage', 'As prescribed'),
                }
            )
            
            # Create the treatment with the medication
            treatment = Treatment.objects.create(
                pet=pet,
                veterinarian=request.user.profile,
                treatment_type='MEDICATION',
                treatment_plan=treatment_description,
                status='COMPLETED',
                scheduled_date=timezone.now(),
                completed_date=timezone.now(),
                medication=medication,
                dosage=request.POST.get('dosage', 'As prescribed'),
                frequency=request.POST.get('frequency', 'As needed'),
                duration=request.POST.get('duration', 'As needed'),
                diagnosis=diagnosis
            )
        
        prescription = request.POST.get('prescription')
        notes = request.POST.get('notes')
        next_visit = request.POST.get('next_visit')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        
        # Create medical record
        record = MedicalRecord.objects.create(
            pet=pet,
            veterinarian=vet_profile,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes,
            next_visit_date=next_visit if next_visit else None
        )
        
        # Add prescription if provided
        if prescription:
            Prescription.objects.create(
                medical_record=record,
                medication_name=prescription,
                dosage='',  
                frequency='',
                duration='',
                instructions=notes or ''
            )
        
        # Create bill if amount is provided
        if amount and due_date:
            BillingRecord.objects.create(
                medical_record=record,
                amount=amount,
                due_date=due_date,
                status='PENDING',
                invoice_number=f'INV-{record.id}-{pet.pet_id}'  # Generate a unique invoice number
            )
        
        messages.success(request, 'Medical record added successfully.')
        return redirect('veterinarians:medical_record_detail', record_id=record.id)
    
    return render(request, 'veterinarians/add_medical_record.html', {
        'pet': pet,
        'today': timezone.now().date()
    })

@login_required
@user_passes_test(is_veterinarian)
def billing_management(request):
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    
    # Get completed appointments that don't have associated medical records with bills
    completed_appointments = Appointment.objects.filter(
        veterinarian=vet_profile,
        status='COMPLETED'
    ).exclude(
        pet__medical_records__billingrecord__isnull=False
    ).select_related(
        'pet',
        'pet__owner'
    ).order_by('-date')
    
    # Get existing bills
    bills = BillingRecord.objects.filter(
        medical_record__veterinarian=vet_profile
    ).select_related(
        'medical_record',
        'medical_record__pet',
        'medical_record__pet__owner'
    ).order_by('-created_at')
    
    # Group bills by status
    pending_bills = bills.filter(status='PENDING')
    paid_bills = bills.filter(status='PAID')
    overdue_bills = bills.filter(status='OVERDUE')
    
    context = {
        'completed_appointments': completed_appointments,
        'pending_bills': pending_bills,
        'paid_bills': paid_bills,
        'overdue_bills': overdue_bills,
        'billing_records': bills
    }
    return render(request, 'veterinarians/billing_management.html', context)

@login_required
@user_passes_test(is_veterinarian)
def update_billing(request, bill_id):
    bill = get_object_or_404(BillingRecord, id=bill_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        bill.status = status
        bill.payment_method = payment_method
        bill.notes = notes
        bill.save()
        
        messages.success(request, 'Bill updated successfully.')
        return redirect('veterinarians:billing_management')
    
    return render(request, 'veterinarians/update_billing.html', {'bill': bill})

@login_required
@user_passes_test(is_veterinarian)
def add_prescription(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    
    if request.method == 'POST':
        medication = request.POST.get('medication')
        dosage = request.POST.get('dosage')
        frequency = request.POST.get('frequency')
        duration = request.POST.get('duration')
        notes = request.POST.get('notes')
        
        Prescription.objects.create(
            medical_record=record,
            medication=medication,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            notes=notes
        )
        
        messages.success(request, 'Prescription added successfully.')
        return redirect('veterinarians:medical_records_detail', record_id=record.id)
    
    return render(request, 'veterinarians/add_prescription.html', {'medical_record': record})

@login_required
@user_passes_test(is_veterinarian)
def add_bill(request, appointment_id):
    def generate_unique_invoice_number():
        while True:
            invoice_number = 'INV-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not BillingRecord.objects.filter(invoice_number=invoice_number).exists():
                return invoice_number

    appointment = get_object_or_404(Appointment, pk=appointment_id)
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        
        # Create the bill with a unique invoice number
        bill = BillingRecord.objects.create(
            medical_record=MedicalRecord.objects.create(
                pet=appointment.pet,
                veterinarian=vet_profile,
                diagnosis='',
                treatment=None,
                notes='',
                next_visit_date=None
            ),
            invoice_number=generate_unique_invoice_number(),
            amount=amount,
            due_date=due_date,
            status='PENDING'
        )
        
        messages.success(request, 'Bill added successfully.')
        return redirect('veterinarians:billing_management')
    
    return render(request, 'veterinarians/add_bill.html', {
        'appointment': appointment,
        'today': timezone.now().date()
    })

@login_required
@user_passes_test(is_veterinarian)
def medical_record_detail(request, record_id):
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    record = get_object_or_404(MedicalRecord, id=record_id, veterinarian=vet_profile)
    
    context = {
        'record': record,
        'pet': record.pet,
        'prescriptions': record.prescription_set.all(),
        'billing_record': record.billingrecord_set.first() if hasattr(record, 'billingrecord_set') else None
    }
    return render(request, 'veterinarians/medical_record_detail.html', context)

@login_required
@user_passes_test(is_veterinarian)
def edit_medical_record(request, record_id):
    vet_profile = get_object_or_404(VeterinarianProfile, profile=request.user.profile)
    record = get_object_or_404(MedicalRecord, id=record_id, veterinarian=vet_profile)
    
    if request.method == 'POST':
        # Update medical record logic
        diagnosis = request.POST.get('diagnosis')
        treatment_description = request.POST.get('treatment', '').strip()
        
        # Create or update medication if treatment description is provided
        if treatment_description:
            # Create or get medication
            medication, _ = Medication.objects.get_or_create(
                name=treatment_description,
                defaults={'description': treatment_description}
            )
            
            # Create or update treatment
            treatment, _ = Treatment.objects.get_or_create(
                pet=record.pet,
                veterinarian=vet_profile.profile,
                treatment_type='MEDICATION',
                defaults={
                    'medication': medication,
                    'scheduled_date': timezone.now(),
                    'status': 'COMPLETED'
                }
            )
            
            # Update treatment if it already exists
            if treatment.medication != medication:
                treatment.medication = medication
                treatment.save()
            
            record.treatment = treatment
        
        notes = request.POST.get('notes')
        next_visit_date = request.POST.get('next_visit_date')
        
        record.diagnosis = diagnosis
        record.notes = notes
        record.next_visit_date = next_visit_date or None
        record.save()
        
        messages.success(request, 'Medical record updated successfully.')
        return redirect('veterinarians:medical_record_detail', record_id=record.id)
    
    # Get available treatments for dropdown
    treatments = Treatment.objects.all()
    
    context = {
        'record': record,
        'pet': record.pet,
        'treatments': treatments
    }
    return render(request, 'veterinarians/edit_medical_record.html', context)

@login_required
def vet_profile(request):
    if request.user.profile.role != 'VET':
        return redirect('registration_login:profile')
    
    veterinarian = request.user.profile.veterinarianprofile
    appointments_count = veterinarian.appointments.count()
    medical_records_count = veterinarian.medicalrecord_set.count()
    pending_bills_count = veterinarian.medicalrecord_set.filter(billingrecord__status='PENDING').count()
    
    context = {
        'veterinarian': veterinarian,
        'appointments_count': appointments_count,
        'medical_records_count': medical_records_count,
        'pending_bills_count': pending_bills_count,
    }
    return render(request, 'veterinarians/profile.html', context)
