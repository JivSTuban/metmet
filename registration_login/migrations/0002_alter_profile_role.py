# Generated by Django 4.2.7 on 2024-11-30 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_login', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('OWNER', 'Pet Owner'), ('VET', 'Veterinarian')], default='OWNER', max_length=10),
        ),
    ]
