# donation_app/views.py

from django.shortcuts import render, redirect
from .forms import DonationForm
from django.http import JsonResponse
from .models import Donor, Donation
from django.db import transaction
from .services.docusign_service import send_docusign_agreement  # Custom service for DocuSign API
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
import threading

def home(request):
    return render(request, 'home.html')

def donate_food(request):
    form = DonationForm()
    return render(request, 'donate_food.html', {'form': form})

def submit_donation(request):
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

                # Save donation details, including pickup date and time
                donation = Donation.objects.create(
                    donor=donor,
                    food_items=form.cleaned_data['food_items'],
                    pickup_address=form.cleaned_data['pickup_address'],
                    city=form.cleaned_data['city'],
                    region=form.cleaned_data['region'],
                    country=form.cleaned_data['country'],
                    postal_code=form.cleaned_data['postal_code'],
                    pickup_date=form.cleaned_data['pickup_date'],  # New field
                    pickup_time=form.cleaned_data['pickup_time'],  # New field
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

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def get_donors(request):
    if request.method == 'GET':
        donors = Donor.objects.all()
        data = [
            {
                'id': donor.id,
                'name': donor.name,
                'email': donor.email,
                'phone': donor.phone,
            }
            for donor in donors
        ]
        return JsonResponse({'status': 'success', 'donors': data})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_donations(request):
    if request.method == 'GET':
        donations = Donation.objects.select_related('donor').all()
        data = [
            {
                'donation_id': donation.id,
                'donor_name': donation.donor.name,
                'donor_email': donation.donor.email,
                'donor_phone': donation.donor.phone,
                'food_items': donation.food_items,
                'pickup_address': donation.pickup_address,
                'city': donation.city,
                'region': donation.region,
                'country': donation.country,
                'postal_code': donation.postal_code,
                'pickup_date': donation.pickup_date.strftime('%Y-%m-%d'),
                'pickup_time': donation.pickup_time.strftime('%H:%M:%S'),
                'agreement_sent': donation.agreement_sent,
                'agreement_signed': donation.agreement_signed,
                'created_at': donation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for donation in donations
        ]
        return JsonResponse({'status': 'success', 'donations': data})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_nonprofit(user):
    return user.groups.filter(name='nonprofit').exists()

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    donors = Donor.objects.all()
    donations = Donation.objects.select_related('donor').all()
    context = {
        'donors': donors,
        'donations': donations,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_nonprofit)
def non_profit_dashboard(request):
    donors = Donor.objects.all()
    donations = Donation.objects.select_related('donor').all()
    context = {
        'donors': donors,
        'donations': donations,
    }
    return render(request, 'non_profit_dashboard.html', context)

def agreement(request):
    if request.method == 'POST':
        return redirect('confirmation')
    return render(request, 'agreement.html')

def confirmation(request):
    return render(request, 'confirmation.html')
