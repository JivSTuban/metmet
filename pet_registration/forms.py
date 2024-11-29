from django import forms
from .models import Pet

SPECIES_CHOICES = [
    ('Dog', 'Dog'),
    ('Cat', 'Cat'),
    ('Bird', 'Bird'),
    ('Fish', 'Fish'),
    ('Hamster', 'Hamster'),
    ('Rabbit', 'Rabbit'),
    ('Guinea Pig', 'Guinea Pig'),
    ('Reptile', 'Reptile'),
    ('Other', 'Other')
]

class PetRegistrationForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['pet_name', 'breed', 'species', 'sex', 'weight', 'birthday', 'pet_description', 'image_url']
        widgets = {
            'pet_name': forms.TextInput(),
            'breed': forms.TextInput(),
            'species': forms.Select(choices=SPECIES_CHOICES),
            'sex': forms.Select(),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pet_description': forms.Textarea(attrs={'class': 'form-control'}),
            'image_url': forms.FileInput(),
        }

class PetUpdateForm(forms.ModelForm):
    class Meta:
        model = Pet
        exclude = ['pet_id', 'owner']  # Exclude both pet_id and owner fields
        widgets = {
            'pet_name': forms.TextInput(),
            'breed': forms.TextInput(),
            'species': forms.Select(choices=SPECIES_CHOICES),
            'sex': forms.Select(),
            'weight': forms.NumberInput(),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pet_description': forms.Textarea(),
            'image_url': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PetUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['birthday'].initial = self.instance.birthday
            self.fields['image_url'].initial = self.instance.image_url