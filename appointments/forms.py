from django import forms
from .models import Appointment
from pet_registration.models import Pet
from veterinarians.models import VeterinarianProfile
from datetime import date

class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    veterinarian = forms.ModelChoiceField(
        queryset=VeterinarianProfile.objects.all(),
        empty_label="Select a veterinarian",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Appointment
        fields = ['pet', 'veterinarian', 'service_type', 'date', 'time', 'reason']
        labels = {
            'service_type': 'Service',
            'reason': 'Notes'
        }
        widgets = {
            'pet': forms.Select(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pet'].queryset = Pet.objects.filter(owner=user)
        self.fields['pet'].empty_label = "Select your pet"

    def clean_date(self):
        appointment_date = self.cleaned_data['date']
        if appointment_date < date.today():
            raise forms.ValidationError("The appointment date cannot be in the past.")
        return appointment_date
