from django.shortcuts import render, redirect
from django.http import HttpResponse

def homepage(request):
    return render(request, 'homepage/homepage.html')

def set_appointment(request):
    if request.method == "POST":
        owner_name = request.POST.get('owner_name')
        pet_name = request.POST.get('pet_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        veterinarian_name = request.POST.get('veterinarian_name')
        reason_for_visit = request.POST.get('reason_for_visit')
        
        # Here you would typically save the appointment to the database
        # Example: Appointment.objects.create(...)
        
        return HttpResponse(f"Appointment for {owner_name}, Pet: {pet_name} set on {appointment_date} at {appointment_time}! Veterianarian is: {veterinarian_name}")
    else:
        return redirect('homepage:index')

def about_us(request):
    return render(request, 'homepage/about.html')
