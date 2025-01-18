# donation_app/forms.py

from django import forms
from .models import Donor, Donation

class DonationForm(forms.Form):
    donor_name = forms.CharField(max_length=255, label="Full Name", required=True)
    donor_email = forms.EmailField(label="Email Address", required=True)
    donor_phone = forms.CharField(max_length=15, label="Phone Number", required=True)
    food_items = forms.JSONField(label="Food Donation Details", required=True)
    pickup_address = forms.CharField(max_length=255, label="Pickup Address", required=True)
    city = forms.CharField(max_length=255, label="City", required=True)
    region = forms.CharField(max_length=255, label="Region/State", required=True)
    country = forms.CharField(max_length=255, label="Country", required=True)
    postal_code = forms.CharField(max_length=10, label="Postal Code", required=True)
    pickup_date = forms.DateField(label="Preferred Pickup Date", required=True)
    pickup_time = forms.TimeField(label="Preferred Pickup Time", required=True)
