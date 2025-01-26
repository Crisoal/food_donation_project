# donation_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import DonationForm
from django.http import JsonResponse
from .models import Donor, Donation, NonprofitProfile
from django.db import transaction
from .services.docusign_service import send_docusign_agreement  # Custom service for DocuSign API
from .services.matching_service import match_donation_to_nonprofit  # Import matching service
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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
                    pickup_date=form.cleaned_data['pickup_date'],
                    pickup_time=form.cleaned_data['pickup_time'],
                )

                # Trigger donation matching process asynchronously
                threading.Thread(
                    target=match_donation_to_nonprofit,
                    args=(donation,)
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

def get_donor(request, donor_id):
    if request.method == 'GET':
        try:
            donor = Donor.objects.get(id=donor_id)
            donations = donor.donation_set.all()

            # Calculate total donations (based on number of donations)
            total_donations = donations.count()

            # Construct donation history
            donation_history = [
                {
                    'date': donation.pickup_date.strftime('%Y-%m-%d'),
                    'amount': sum(item['quantity'] for item in donation.food_items.values())  # Example sum logic
                }
                for donation in donations
            ]

            # Prepare response data
            data = {
                'id': donor.id,
                'name': donor.name,
                'email': donor.email,
                'phone': donor.phone,
                'total_donations': total_donations,
                'donation_history': donation_history
            }
            return JsonResponse({'status': 'success', 'donor': data})
        except Donor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Donor not found'})
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

def add_donor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if name and email and phone:
            donor = Donor.objects.create(name=name, email=email, phone=phone, address=address)
            return JsonResponse({'status': 'success', 'message': 'Donor added successfully'})
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Edit Donor
def edit_donor(request, donor_id):
    if request.method == 'PUT':
        import json
        data = json.loads(request.body)

        try:
            donor = Donor.objects.get(id=donor_id)
            donor.name = data.get('name', donor.name)
            donor.email = data.get('email', donor.email)
            donor.phone = data.get('phone', donor.phone)
            # donor.address = data.get('address', donor.address)
            donor.save()

            return JsonResponse({'status': 'success', 'message': 'Donor updated successfully'})
        except Donor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Donor not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def delete_donor(request, donor_id):
    if request.method == 'POST':
        try:
            donor = Donor.objects.get(id=donor_id)
            donor.delete()
            return JsonResponse({'status': 'success', 'message': 'Donor deleted successfully'})
        except Donor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Donor not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@receiver(post_save, sender=Donation)
def update_total_donations_on_save(sender, instance, **kwargs):
    donor = instance.donor
    donor.total_donations = donor.donation_set.count()
    donor.save()

@receiver(post_delete, sender=Donation)
def update_total_donations_on_delete(sender, instance, **kwargs):
    donor = instance.donor
    donor.total_donations = donor.donation_set.count()
    donor.save()

def is_admin(user):
    return user.groups.filter(name='admin').exists()

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

# Check if the user is in the 'nonprofit' group
def is_nonprofit(user):
    return user.groups.filter(name='nonprofit').exists()

@login_required
@user_passes_test(is_nonprofit)
def non_profit_dashboard(request):
    try:
        nonprofit_profile = NonprofitProfile.objects.get(user=request.user)
    except NonprofitProfile.DoesNotExist:
        messages.error(request, "No profile found for your account. Please contact support.")
        return redirect('home')  # Redirect to a safe page

    donations = Donation.objects.filter(matched_nonprofit=nonprofit_profile)
    donors = Donor.objects.filter(donation__matched_nonprofit=nonprofit_profile).distinct()

    context = {
        'nonprofit_profile': nonprofit_profile,
        'donations': donations,
        'donors': donors,
    }

    return render(request, 'non_profit_dashboard.html', context)


@login_required
@user_passes_test(is_nonprofit)
def fetch_nonprofit_profile(request):
    """
    API endpoint to fetch nonprofit profile details for logged-in nonprofit users.
    """
    nonprofit_profile = get_object_or_404(NonprofitProfile, user=request.user)

    # Return profile details as JSON
    data = {
        'organization_name': nonprofit_profile.organization_name,
        'mission_statement': nonprofit_profile.mission_statement,
        'address': nonprofit_profile.address,
        'contact_number': nonprofit_profile.contact_number,
        'city': nonprofit_profile.city,
        'state': nonprofit_profile.state,
        'country': nonprofit_profile.country,
        'areas_of_operation': nonprofit_profile.areas_of_operation.split(','),  # Convert to list
        'requirements_or_preferences': nonprofit_profile.requirements_or_preferences,
        'capacity': nonprofit_profile.capacity,
    }

    return JsonResponse(data)


def agreement(request):
    if request.method == 'POST':
        return redirect('confirmation')
    return render(request, 'agreement.html')

def confirmation(request):
    return render(request, 'confirmation.html')
