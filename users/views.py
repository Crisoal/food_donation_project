# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        # Log the user in
        login(self.request, form.get_user())

        # Redirect based on group membership
        user = form.get_user()
        if user.groups.filter(name='admin').exists():
            return redirect('admin_dashboard')
        elif user.groups.filter(name='nonprofit').exists():
            return redirect('non_profit_dashboard')
        else:
            return redirect('home')  # Default redirect

    def form_invalid(self, form):
        # Handle invalid login attempt
        messages.error(self.request, "Invalid username or password.")
        return redirect('login')  # Redirect to login page

    def get(self, request, *args, **kwargs):
        # Ensure unauthenticated users can access the login page
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    """
    Custom LogoutView to handle post-logout redirection.
    """
    def dispatch(self, request, *args, **kwargs):
        # You can add custom actions here if needed
        response = super().dispatch(request, *args, **kwargs)
        return redirect('login')  # Redirect to login page after logout


def create_default_users():
    User = get_user_model()

    # Create admin_user
    admin_user, created = User.objects.get_or_create(
        username='admin_user',
        defaults={'email': 'admin@donatetofeed.com'}
    )
    if created:
        admin_user.set_password('admin246')
        admin_user.save()
        print("Admin user created!")

    # Create nonprofit_user
    nonprofit_user, created = User.objects.get_or_create(
        username='nonprofit_user',
        defaults={'email': 'apinkenonprofit@donatetofeed.com'}
    )
    if created:
        nonprofit_user.set_password('apinkeNonprofit26')
        nonprofit_user.save()
        print("Nonprofit user created!")
