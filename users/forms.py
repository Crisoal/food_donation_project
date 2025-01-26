# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from donation_app.models import NonprofitProfile

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class NonprofitProfileForm(forms.ModelForm):
    class Meta:
        model = NonprofitProfile
        fields = ['organization_name', 'mission_statement', 'address', 'contact_number', 
                  'city', 'state', 'country', 'areas_of_operation', 'requirements_or_preferences', 'capacity']
