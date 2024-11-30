from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
import logging
import traceback

from veterinarians.models import BillingRecord

logger = logging.getLogger(__name__)

@login_required
def billing_list(request):
    try:
        # Get all bills for the current user's profile
        bills = BillingRecord.objects.filter(
            medical_record__pet__owner=request.user
        ).order_by('-created_at')
        
        # Debug logging
        logger.info(f"Total bills found: {bills.count()}")
        for bill in bills:
            logger.info(f"Bill ID: {bill.id}, Status: {bill.status}, Status Display: {bill.get_status_display()}")
        
        # Add a message if no bills are found
        if not bills.exists():
            messages.info(request, "You currently have no billing records.")
        
        context = {
            'bills': bills,
        }
        return render(request, 'billings/billing_list.html', context)
    
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Billing list error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Provide a user-friendly error message
        messages.error(request, "An error occurred while retrieving your billing records. Please try again later.")
        
        return render(request, 'billings/billing_list.html', {
            'bills': [], 
            'error': "Unable to retrieve billing records"
        })

@login_required
def bill_details(request, bill_id):
    try:
        # Retrieve the specific bill, ensuring it belongs to the current user
        bill = get_object_or_404(
            BillingRecord, 
            id=bill_id, 
            medical_record__pet__owner=request.user
        )
        
        context = {
            'bill': bill,
            'medical_record': bill.medical_record,
            'pet': bill.medical_record.pet,
        }
        
        return render(request, 'billings/bill_details.html', context)
    
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Bill details error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Provide a user-friendly error message
        messages.error(request, "An error occurred while retrieving the bill details. Please try again later.")
        
        return render(request, 'billings/billing_list.html', {
            'error': "Unable to retrieve bill details"
        })

@login_required
def process_payment(request, bill_id):
    try:
        if request.method != 'POST':
            messages.error(request, "Invalid request method.")
            return redirect('billings:billing_list')

        # Get the bill and verify ownership
        bill = get_object_or_404(
            BillingRecord, 
            id=bill_id, 
            medical_record__pet__owner=request.user,
            status__in=['PENDING', 'OVERDUE']  # Only allow payment for pending or overdue bills
        )

        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect('billings:bill_details', bill_id=bill_id)

        # Process the payment
        bill.mark_as_paid(payment_method)
        
        messages.success(request, f"Payment processed successfully for bill #{bill.invoice_number}")
        return redirect('billings:billing_list')

    except BillingRecord.DoesNotExist:
        messages.error(request, "Bill not found or you don't have permission to pay this bill.")
        return redirect('billings:billing_list')
    
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, "An error occurred while processing the payment. Please try again later.")
        return redirect('billings:bill_details', bill_id=bill_id)
