from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Treatment, Medication, Procedure, TreatmentReminder
from pet_registration.models import Pet
from django.forms import ModelForm, DateTimeField, widgets
from django.core.exceptions import ValidationError

class TreatmentForm(ModelForm):
    scheduled_date = DateTimeField(widget=widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    next_visit = DateTimeField(widget=widgets.DateTimeInput(attrs={'type': 'datetime-local'}), required=False)
    
    class Meta:
        model = Treatment
        fields = [
            'pet', 'treatment_type', 'scheduled_date', 'next_visit',
            'symptoms', 'diagnosis', 'treatment_plan', 'recommendations',
            'medication', 'procedure', 'dosage', 'frequency', 'duration',
            'procedure_notes'
        ]
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.profile.is_vet:
            # For pet owners, only show their pets
            self.fields['pet'].queryset = Pet.objects.filter(owner=user.profile)
        elif user and user.profile.is_vet:
            # For vets, show all pets
            self.fields['pet'].queryset = Pet.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        medication = cleaned_data.get('medication')
        procedure = cleaned_data.get('procedure')
        
        if medication and procedure:
            raise ValidationError("A treatment can't be both a medication and a procedure.")
        if not medication and not procedure:
            raise ValidationError("Please select either a medication or a procedure.")
            
        return cleaned_data

@login_required
def treatment_list(request):
    if request.user.profile.is_vet:
        # Vets see all treatments they're responsible for
        treatments = Treatment.objects.filter(veterinarian=request.user.profile).order_by('-scheduled_date')
    else:
        # Pet owners see treatments for their pets
        pets = Pet.objects.filter(owner=request.user.profile)
        treatments = Treatment.objects.filter(pet__in=pets).order_by('-scheduled_date')
    
    # Separate treatments by status
    upcoming_treatments = treatments.filter(status='SCHEDULED')
    ongoing_treatments = treatments.filter(status='IN_PROGRESS')
    completed_treatments = treatments.filter(status='COMPLETED')
    
    context = {
        'upcoming_treatments': upcoming_treatments,
        'ongoing_treatments': ongoing_treatments,
        'completed_treatments': completed_treatments,
        'is_vet': request.user.profile.is_vet
    }
    return render(request, 'treatments/treatment_list.html', context)

@login_required
def treatment_detail(request, treatment_id):
    # Check if user is vet or pet owner
    if request.user.profile.is_vet:
        treatment = get_object_or_404(Treatment, id=treatment_id)
    else:
        treatment = get_object_or_404(Treatment, id=treatment_id, pet__owner=request.user.profile)
    
    reminders = treatment.reminders.all().order_by('reminder_date')
    context = {
        'treatment': treatment,
        'reminders': reminders,
        'is_vet': request.user.profile.is_vet
    }
    return render(request, 'treatments/treatment_detail.html', context)

@login_required
def add_treatment(request):
    # Only vets can add treatments
    if not request.user.profile.is_vet:
        raise PermissionDenied("Only veterinarians can add treatments.")
        
    if request.method == 'POST':
        form = TreatmentForm(request.POST, user=request.user)
        if form.is_valid():
            treatment = form.save(commit=False)
            treatment.veterinarian = request.user.profile
            treatment.save()
            
            # Create reminder for the treatment
            TreatmentReminder.objects.create(
                treatment=treatment,
                reminder_date=treatment.scheduled_date,
                reminder_type='UPCOMING',
                message=f"Upcoming {treatment.get_treatment_type_display()} for {treatment.pet.name}"
            )
            
            # If next visit is scheduled, create a reminder
            if treatment.next_visit:
                TreatmentReminder.objects.create(
                    treatment=treatment,
                    reminder_date=treatment.next_visit,
                    reminder_type='FOLLOWUP',
                    message=f"Follow-up visit for {treatment.pet.name}"
                )
            
            messages.success(request, 'Treatment added successfully.')
            return redirect('treatments:treatment_detail', treatment_id=treatment.id)
    else:
        form = TreatmentForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Add New Treatment',
        'button_text': 'Add Treatment'
    }
    return render(request, 'treatments/treatment_form.html', context)

@login_required
def update_treatment(request, treatment_id):
    # Check if user is vet or pet owner
    if request.user.profile.is_vet:
        treatment = get_object_or_404(Treatment, id=treatment_id)
    else:
        treatment = get_object_or_404(Treatment, id=treatment_id, pet__owner=request.user.profile)
    
    if request.method == 'POST':
        form = TreatmentForm(request.POST, instance=treatment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treatment updated successfully.')
            return redirect('treatments:treatment_detail', treatment_id=treatment.id)
    else:
        form = TreatmentForm(instance=treatment, user=request.user)
    
    context = {
        'form': form,
        'title': 'Update Treatment',
        'button_text': 'Update Treatment'
    }
    return render(request, 'treatments/treatment_form.html', context)

@login_required
def pet_treatment_history(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user.profile)
    treatments = Treatment.objects.filter(pet=pet).order_by('-scheduled_date')
    
    # Group treatments by type (medication/procedure)
    medication_treatments = treatments.filter(medication__isnull=False)
    procedure_treatments = treatments.filter(procedure__isnull=False)
    
    context = {
        'pet': pet,
        'medication_treatments': medication_treatments,
        'procedure_treatments': procedure_treatments,
    }
    return render(request, 'treatments/pet_treatment_history.html', context)

@login_required
def update_treatment_status(request, treatment_id):
    if request.method != 'POST':
        return redirect('treatments:treatment_list')
        
    # Check if user is vet or pet owner
    if request.user.profile.is_vet:
        treatment = get_object_or_404(Treatment, id=treatment_id)
    else:
        treatment = get_object_or_404(Treatment, id=treatment_id, pet__owner=request.user.profile)
    
    new_status = request.POST.get('status')
    
    if new_status in dict(Treatment.STATUS_CHOICES):
        treatment.status = new_status
        if new_status == 'COMPLETED':
            treatment.completed_date = timezone.now()
        treatment.save()
        messages.success(request, 'Treatment status updated successfully.')
    else:
        messages.error(request, 'Invalid status provided.')
        
    return redirect('treatments:treatment_detail', treatment_id=treatment_id)

@login_required
def add_treatment_note(request, treatment_id):
    if request.method != 'POST':
        return redirect('treatments:treatment_list')
        
    # Check if user is vet or pet owner
    if request.user.profile.is_vet:
        treatment = get_object_or_404(Treatment, id=treatment_id)
    else:
        treatment = get_object_or_404(Treatment, id=treatment_id, pet__owner=request.user.profile)
    
    note = request.POST.get('note')
    
    if note:
        if treatment.medication:
            treatment.notes = (treatment.notes + '\n\n' + note).strip()
        else:
            treatment.procedure_notes = (treatment.procedure_notes + '\n\n' + note).strip()
        treatment.save()
        messages.success(request, 'Note added successfully.')
    else:
        messages.error(request, 'Note cannot be empty.')
        
    return redirect('treatments:treatment_detail', treatment_id=treatment_id)

@login_required
def medication_list(request):
    medications = Medication.objects.all().order_by('name')
    context = {'medications': medications}
    return render(request, 'treatments/medication_list.html', context)

@login_required
def procedure_list(request):
    procedures = Procedure.objects.all().order_by('name')
    context = {'procedures': procedures}
    return render(request, 'treatments/procedure_list.html', context)
