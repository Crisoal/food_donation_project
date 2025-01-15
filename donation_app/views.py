from django.shortcuts import render, redirect
from .forms import DonationForm
from .models import Donation

def home(request):
    return render(request, 'home.html')

def donate_food(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            # Assume donor is logged in
            donor = request.user
            donation.donor = donor
            donation.save()
            return redirect('agreement')
    else:
        form = DonationForm()
    return render(request, 'donate_food.html', {'form': form})

def agreement(request):
    if request.method == 'POST':
        return redirect('confirmation')
    return render(request, 'agreement.html')

def confirmation(request):
    return render(request, 'confirmation.html')
