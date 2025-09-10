from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from django.dispatch import receiver
from django.db.models import Index
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    """
    Custom User model for Safari & Bush Retreats.
    - Extends AbstractUser with phone, nationality, profile, preferences and small helpers.
    - Note: email is unique by default here — see migration caution below.
    """
    ROLE_CHOICES = [
        ('tourist', _('Tourist')),
        ('guide', _('Tour Guide')),
        ('admin', _('Administrator')),
        ('content_manager', _('Content Manager')),
    ]

    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say')),
    ]

    # Consider whether you want email unique — changing this on an existing project requires careful migration.
    email = models.EmailField(_('email address'), unique=True)

    # Basic information
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tourist', db_index=True)
    phone_number = PhoneNumberField(blank=True, null=True, db_index=True)  # stored in E.164
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    nationality = CountryField(blank=True, null=True)

    # Profile info
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    # Travel preferences
    preferred_language = models.CharField(max_length=10, default='en')
    dietary_requirements = models.TextField(blank=True)
    accessibility_needs = models.TextField(blank=True)
    travel_experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', _('Beginner')),
            ('intermediate', _('Intermediate')),
            ('advanced', _('Advanced')),
            ('expert', _('Expert')),
        ],
        default='beginner'
    )

    preferred_accommodation_type = models.CharField(
        max_length=20,
        choices=[
            ('budget', _('Budget')),
            ('standard', _('Standard')),
            ('luxury', _('Luxury')),
        ],
        blank=True
    )

    # Verification & settings
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
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            Index(fields=['email']),
            Index(fields=['phone_number']),
            Index(fields=['role']),
        ]

    def __str__(self):
        email = self.email or _('no-email')
        return f"{self.get_full_name() or self.username} ({email})"

    def get_full_name(self):
        """Return first_name plus last_name, or username if blank."""
        parts = [self.first_name or '', self.last_name or '']
        full_name = ' '.join(p for p in parts if p).strip()
        return full_name or self.username

    def get_display_name(self):
        """Short public display name."""
        return self.first_name or self.username

    @property
    def age(self):
        """Compute age in years from date_of_birth (None if not set)."""
        if not self.date_of_birth:
            return None
        today = date.today()
        dob = self.date_of_birth
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return years

    def clean(self):
        """Small hook for normalization/validation before save (phonenumber_field handles phone validation)."""
        super().clean()
        # Example normalization (uncomment if you need it)
        # if self.nationality:
        #     self.nationality = str(self.nationality).upper()

    def get_contact_number(self):
        """Return a string contact number or None."""
        return str(self.phone_number) if self.phone_number else None


class UserProfile(models.Model):
    """Extended profile information for users."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = PhoneNumberField(blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)

    # Travel document information
    passport_number = models.CharField(max_length=50, blank=True)
    passport_expiry = models.DateField(blank=True, null=True)
    passport_issuing_country = CountryField(blank=True, null=True)

    # Medical information
    medical_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    allergies = models.TextField(blank=True)

    # Travel insurance
    has_travel_insurance = models.BooleanField(default=False)
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"
    

# Signal: create the related profile automatically when a CustomUser is created.
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

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