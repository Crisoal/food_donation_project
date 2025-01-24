# donation_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donate-food/', views.donate_food, name='donate_food'),  # This renders the form
    path('submit-donation/', views.submit_donation, name='submit_donation'),  # This handles form submission
    path('agreement/', views.agreement, name='agreement'),
    path('confirmation/', views.confirmation, name='confirmation'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('get-donors/', views.get_donors, name='get_donors'),
    path('get-donations/', views.get_donations, name='get_donations'),

    # Non Profit
    path('non-profit/', views.non_profit_dashboard, name='non_profit_dashboard'),

    # Logistics
    path('logistics/', views.logistics_dashboard, name='logistics_dashboard'),
]
