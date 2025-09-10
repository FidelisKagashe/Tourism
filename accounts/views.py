from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction
import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, UserProfile, UserActivityLog
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm, UserProfileForm, ExtendedProfileForm
from bookings.models import Booking
from reviews.models import Review
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.auth.forms import PasswordResetForm

logger = logging.getLogger(__name__)

class UserRegistrationView(CreateView):
    """User registration view with post-save side effects (logging, email, auto-login)."""
    model = CustomUser
    form_class = CustomUserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')

    @transaction.atomic
    def form_valid(self, form):
        # Save the user using the form's save() (will hash the password)
        user = form.save()

        # IMPORTANT: set self.object so get_success_url() can use it safely
        self.object = user

        # Try to log the activity; keep failure non-fatal but log it
        try:
            UserActivityLog.objects.create(
                user=user,
                action_type='register',
                description='New user registration',
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:512],
            )
        except Exception as exc:
            logger.exception("Failed to create UserActivityLog for user %s: %s", getattr(user, 'pk', 'unknown'), exc)

        # Send welcome email (fail_silently True to avoid breaking registration)
        if user.email:
            try:
                send_mail(
                    subject='Welcome to Tanzania Safari Adventures!',
                    message=(
                        f'Hello {user.first_name or user.username},\n\n'
                        "Welcome to Tanzania Safari Adventures! We're excited to help you "
                        "plan your dream safari experience."
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as exc:
                logger.exception("Failed to send welcome email to %s: %s", user.email, exc)

        # Log the user in (creates session)
        login(self.request, user)

        messages.success(self.request, 'Registration successful! Welcome to Tanzania Safari Adventures!')

        # Redirect to the success URL — safe now because self.object is set
        return redirect(self.get_success_url())

    def get_client_ip(self):
        """Get the IP address of the client (handles proxies)."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR', '')
        return ip

def user_login(request):
    """User login view."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                remember_me = request.POST.get('remember_me')
                if remember_me:
                    request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                else:
                    request.session.set_expiry(0)  # Browser session
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                next_url = request.GET.get('next', 'core:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout view."""
    user = request.user
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:home')

class UserDashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard view."""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's bookings
        bookings = Booking.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Get user's reviews
        reviews = Review.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Get recent activity
        activities = UserActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
        
        # Statistics
        total_bookings = Booking.objects.filter(user=user).count()
        completed_tours = Booking.objects.filter(user=user, booking_status='completed').count()
        total_reviews = Review.objects.filter(user=user).count()
        
        context.update({
            'bookings': bookings,
            'reviews': reviews,
            'activities': activities,
            'total_bookings': total_bookings,
            'completed_tours': completed_tours,
            'total_reviews': total_reviews,
        })
        
        return context

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """User profile update view."""
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        
        # Log profile update
        UserActivityLog.objects.create(
            user=self.request.user,
            action_type='profile_update',
            description='Profile information updated',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        return super().form_valid(form)
    
    def get_client_ip(self):
        """Get client IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class ExtendedProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Extended profile update view."""
    model = UserProfile
    form_class = ExtendedProfileForm
    template_name = 'accounts/extended_profile_update.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Extended profile updated successfully!')
        
        # Log profile update
        UserActivityLog.objects.create(
            user=self.request.user,
            action_type='profile_update',
            description='Extended profile information updated',
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        return super().form_valid(form)
    
    def get_client_ip(self):
        """Get client IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

@login_required
def user_bookings(request):
    """User bookings view."""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/user_bookings.html', {'bookings': bookings})

@login_required
def user_reviews(request):
    """User reviews view."""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/user_reviews.html', {'reviews': reviews})

@login_required
def user_documents(request):
    """User travel documents view."""
    documents = request.user.travel_documents.all().order_by('-created_at')
    return render(request, 'accounts/user_documents.html', {'documents': documents})

# ---- Password reset CBVs ----
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'                # <- your current file
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = PasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'