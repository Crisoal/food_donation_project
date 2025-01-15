from django.db import models

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    delivery_address = models.TextField()
    agreement_signed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
