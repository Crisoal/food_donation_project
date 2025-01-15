# food_donation/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('donation_app.urls')),  # Routes for donation app
    path('users/', include('users.urls')),   # Routes for user authentication
]
