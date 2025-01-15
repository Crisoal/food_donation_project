from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donate-food/', views.donate_food, name='donate_food'),
    path('agreement/', views.agreement, name='agreement'),
    path('confirmation/', views.confirmation, name='confirmation'),
]
