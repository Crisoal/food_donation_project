# donation_app/models.py

from django.db import models
from django.utils import timezone

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    total_donations = models.PositiveIntegerField(default=0)  # New field

class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    food_items = models.JSONField()
    pickup_address = models.TextField()
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    agreement_sent = models.BooleanField(default=False)
    agreement_signed = models.BooleanField(default=False)
    pickup_date = models.DateField(default=timezone.now)  # Default is current date
    pickup_time = models.TimeField(default=timezone.now)  # Default is current time
    created_at = models.DateTimeField(auto_now_add=True)
