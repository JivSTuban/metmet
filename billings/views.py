from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from appointments.models import Bill

@login_required
def billing_list(request):
    # Get all bills for appointments owned by the current user
    bills = Bill.objects.filter(
        appointment__owner__user=request.user
    ).order_by('-created_at')
    
    context = {
        'bills': bills,
    }
    return render(request, 'billings/billing_list.html', context)
