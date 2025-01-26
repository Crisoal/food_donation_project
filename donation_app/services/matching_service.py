# donation_app/services/matching_service.py

from django.db.models import Q
from donation_app.models import Donation, NonprofitProfile
from django.core.mail import send_mail  # For sending email notifications

def match_donation_to_nonprofit(donation):
    print(f"Starting to match donation {donation.id} to a nonprofit.")

    # Step 1: Filter non-profits based on the 'areas_of_operation' field
    location_match = NonprofitProfile.objects.filter(
        Q(areas_of_operation__icontains=donation.city) |
        Q(areas_of_operation__icontains=donation.region) |
        Q(areas_of_operation__icontains=donation.country)
    )
    print(f"Nonprofits filtered by areas of operation: {location_match.count()} found.")

    # Step 2: Filter non-profits based on the 'requirements_or_preferences' field for food types
    perishable_status = donation.get_perishable_status()
    print(f"Perishable status for this donation: {perishable_status}")
    
    matching_nonprofits = location_match.filter(
        Q(requirements_or_preferences__icontains=perishable_status)
    )
    print(f"Nonprofits filtered by food type preference: {matching_nonprofits.count()} found.")

    # Step 3: Check if a match is found
    if matching_nonprofits.exists():
        # Assign the first matching non-profit
        nonprofit = matching_nonprofits.first()
        print(f"Matching nonprofit found: {nonprofit.organization_name}")
        
        donation.matched_nonprofit = nonprofit
        donation.status = 'assigned'
        donation.save()

        # # Send notification to the nonprofit
        # send_notification(nonprofit)
    else:
        # If no match found, leave donation in "pending" state
        print("No matching nonprofit found. Donation status set to 'pending'.")
        donation.status = 'pending'
        donation.save()

# def send_notification(nonprofit):
#     # Send an email notification to the non-profit
#     send_mail(
#         'New Donation Matched',
#         f'Your organization, {nonprofit.organization_name}, has been matched with a new donation.',
#         'no-reply@donationapp.com',
#         [nonprofit.user.email],
#         fail_silently=False,
#     )
#     print(f"Notification sent to {nonprofit.organization_name} at {nonprofit.user.email}")
