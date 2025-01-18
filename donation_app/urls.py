# donation_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donate-food/', views.donate_food, name='donate_food'),  # This renders the form
    path('submit-donation/', views.submit_donation, name='submit_donation'),  # This handles form submission
    path('agreement/', views.agreement, name='agreement'),
    path('confirmation/', views.confirmation, name='confirmation'),
]
