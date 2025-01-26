# donation_app/models.py

from django.db import models
from users.models import CustomUser
from django.utils import timezone  

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    total_donations = models.PositiveIntegerField(default=0)  # New field

# donation_app/models.py

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
    pickup_date = models.DateField(default=timezone.now)
    pickup_time = models.TimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Assigned Nonprofit
    matched_nonprofit = models.ForeignKey('NonprofitProfile', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default='pending')  # 'pending', 'assigned', 'completed'
    perishable_status = models.CharField(max_length=20, default='Non-perishable')  # New field for perishable status

    def __str__(self):
        return f"Donation {self.id} - {self.status}"

    def save(self, *args, **kwargs):
        # Automatically determine and set the perishable status when saving
        self.perishable_status = self.get_perishable_status()
        super().save(*args, **kwargs)

    def get_perishable_status(self):
        """
        Determines if any food item in this donation is perishable based on the food_type.
        If any food item is perishable (e.g., Meat, Fruits, Vegetables), it will return 'Perishable'.
        If none are perishable, it returns 'Non-perishable'.
        """
        perishable_foods = ['Meat', 'Fruits', 'Vegetables']
        
        # Loop through food_items to check if any of them are perishable
        for item in self.food_items:
            food_type = item.get('food_type', '')
            if food_type in perishable_foods:
                return 'Perishable'  # If any item is perishable, return 'Perishable'
        
        return 'Non-perishable'  # If none of the items are perishable, return 'Non-perishable'


class NonprofitProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='nonprofit_profile')
    organization_name = models.CharField(max_length=255)
    mission_statement = models.TextField()
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    areas_of_operation = models.TextField()  # A comma-separated list of regions or areas
    requirements_or_preferences = models.TextField()  # Details about the food/goods they accept
    capacity = models.PositiveIntegerField()  # Maximum number of donations they can handle in a given period

    def __str__(self):
        return self.organization_name
