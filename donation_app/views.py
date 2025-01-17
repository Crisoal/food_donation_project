# donation_app/views.py

from django.shortcuts import render, redirect
from .forms import DonationForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Donor, Donation
from django.db import transaction
from .services.docusign_service import send_docusign_agreement  # Custom service for DocuSign API
import threading

def home(request):
    return render(request, 'home.html')

def donate_food(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Save donor details
                donor, created = Donor.objects.get_or_create(
                    email=form.cleaned_data['donor_email'],
                    defaults={
                        'name': form.cleaned_data['donor_name'],
                        'phone': form.cleaned_data['donor_phone'],
                    }
                )

                # Save donation details
                donation = Donation.objects.create(
                    donor=donor,
                    food_items=form.cleaned_data['food_items'],
                    pickup_address=form.cleaned_data['pickup_address'],
                    city=form.cleaned_data['city'],
                    region=form.cleaned_data['region'],
                    country=form.cleaned_data['country'],
                    postal_code=form.cleaned_data['postal_code'],
                )

            # Send agreement asynchronously
            threading.Thread(
                target=send_docusign_agreement,
                args=(donor, donation)
            ).start()

            return JsonResponse({
                'status': 'success',
                'message': f"An agreement form has been sent to {donor.email}. Please check your email and sign the agreement to complete the donation."
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = DonationForm()
    return render(request, 'donate_food.html', {'form': form})


def agreement(request):
    if request.method == 'POST':
        return redirect('confirmation')
    return render(request, 'agreement.html')

def confirmation(request):
    return render(request, 'confirmation.html')
