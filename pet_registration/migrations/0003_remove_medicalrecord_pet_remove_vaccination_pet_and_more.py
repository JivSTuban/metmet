# Generated by Django 4.2.7 on 2024-11-30 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pet_registration', '0002_pet_primary_veterinarian'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicalrecord',
            name='pet',
        ),
        migrations.RemoveField(
            model_name='vaccination',
            name='pet',
        ),
        migrations.DeleteModel(
            name='MedicalFile',
        ),
        migrations.DeleteModel(
            name='MedicalRecord',
        ),
        migrations.DeleteModel(
            name='Vaccination',
        ),
    ]