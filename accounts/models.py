from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    """Custom User model extending AbstractUser with tourism-specific fields."""
    
    ROLE_CHOICES = [
        ('tourist', 'Tourist'),
        ('guide', 'Tour Guide'),
        ('admin', 'Administrator'),
        ('content_manager', 'Content Manager'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    # Basic Information
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tourist')
    phone_number = PhoneNumberField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    nationality = CountryField(blank=True, null=True)
    
    # Profile Information
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Travel Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    dietary_requirements = models.TextField(blank=True)
    accessibility_needs = models.TextField(blank=True)
    travel_experience_level = models.CharField(
        max_length=20, 
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert')
        ],
        default='beginner'
    )
    
    # Preferences
    preferred_accommodation_type = models.CharField(
        max_length=20,
        choices=[
            ('budget', 'Budget'),
            ('standard', 'Standard'),
            ('luxury', 'Luxury')
        ],
        blank=True
    )
    
    # Verification and Settings
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'accounts_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_display_name(self):
        """Return display name for public use."""
        if self.first_name:
            return self.first_name
        return self.username

class UserProfile(models.Model):
    """Extended profile information for users."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = PhoneNumberField(blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Travel Document Information
    passport_number = models.CharField(max_length=20, blank=True)
    passport_expiry = models.DateField(blank=True, null=True)
    passport_issuing_country = CountryField(blank=True, null=True)
    
    # Medical Information
    medical_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    
    # Travel Insurance
    has_travel_insurance = models.BooleanField(default=False)
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

class TravelDocument(models.Model):
    """Travel documents uploaded by users."""
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('vaccination', 'Vaccination Certificate'),
        ('insurance', 'Travel Insurance'),
        ('driving_license', 'Driving License'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='travel_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='travel_documents/')
    expiry_date = models.DateField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_traveldocument'
        verbose_name = 'Travel Document'
        verbose_name_plural = 'Travel Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.document_name}"

class UserActivityLog(models.Model):
    """Log user activities for security and analytics."""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('booking_create', 'Booking Created'),
        ('booking_cancel', 'Booking Cancelled'),
        ('payment_made', 'Payment Made'),
        ('review_posted', 'Review Posted'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_useractivitylog'
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.timestamp}"