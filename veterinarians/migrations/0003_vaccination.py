# Generated by Django 4.2.7 on 2024-11-30 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pet_registration', '0003_remove_medicalrecord_pet_remove_vaccination_pet_and_more'),
        ('veterinarians', '0002_billingrecord_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vaccination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vaccine_name', models.CharField(max_length=100)),
                ('date_administered', models.DateField()),
                ('next_due_date', models.DateField()),
                ('batch_number', models.CharField(blank=True, max_length=50, null=True)),
                ('notes', models.TextField(blank=True)),
                ('pet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vaccinations', to='pet_registration.pet')),
                ('veterinarian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='veterinarians.veterinarianprofile')),
            ],
            options={
                'ordering': ['-date_administered'],
            },
        ),
    ]