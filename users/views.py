# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm, NonprofitProfileForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        nonprofit_form = NonprofitProfileForm(request.POST)
        if form.is_valid() and nonprofit_form.is_valid():
            # Create user
            user = form.save()

            # Add user to nonprofit group
            nonprofit_group, _ = Group.objects.get_or_create(name='nonprofit')
            user.groups.add(nonprofit_group)
            user.save()

            # Log the user in
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
        nonprofit_form = NonprofitProfileForm()
    
    return render(request, 'register.html', {'form': form, 'nonprofit_form': nonprofit_form})

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Points to the login form template

    def form_valid(self, form):
        """
        Handle successful login.
        """
        user = form.get_user()
        login(self.request, user)

        # Redirect user based on their group
        if user.groups.filter(name='admin').exists():
            return redirect('admin_dashboard')  # Admin's dashboard
        elif user.groups.filter(name='nonprofit').exists():
            return redirect('non_profit_dashboard')  # Nonprofit's dashboard
        else:
            return redirect('home')  # Default for other users without a specific group

    def get(self, request, *args, **kwargs):
        """
        Override GET method to handle redirection for already authenticated users.
        """
        if request.user.is_authenticated:
            # Redirect authenticated users to their respective dashboards
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        """
        Determine the post-login redirect URL.
        """
        user = self.request.user
        if user.groups.filter(name='admin').exists():
            return 'admin_dashboard'  # Admin dashboard URL name
        elif user.groups.filter(name='nonprofit').exists():
            return 'non_profit_dashboard'  # Nonprofit dashboard URL name
        return 'home'  # Default homepage URL name

class CustomLogoutView(LogoutView):
    """
    Custom LogoutView to handle post-logout redirection.
    """
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return redirect('login')  # Redirect to login page after logout
