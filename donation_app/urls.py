# donation_app/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from users.views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('donate-food/', views.donate_food, name='donate_food'),
    path('submit-donation/', views.submit_donation, name='submit_donation'),
    path('agreement/', views.agreement, name='agreement'),
    path('confirmation/', views.confirmation, name='confirmation'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin/Donors
    path('get-donors/', views.get_donors, name='get_donors'),
    path('get-donor/<int:donor_id>/', views.get_donor, name='get_donor'),
    path('add-donor/', views.add_donor, name='add_donor'),
    path('edit-donor/<int:donor_id>/', views.edit_donor, name='edit_donor'),
    path('delete-donor/<int:donor_id>/', views.delete_donor, name='delete_donor'),
    
    # Admin/Donations
    path('get-donations/', views.get_donations, name='get_donations'),

    # Non-Profit
    path('non-profit-dashboard/', views.non_profit_dashboard, name='non_profit_dashboard'),
    path('api/nonprofit/profile/', views.fetch_nonprofit_profile, name='fetch_nonprofit_profile'),
    path('api/donations/<int:donation_id>/', views.fetch_donation_details, name='fetch_donation_details'),

    # Auth
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
