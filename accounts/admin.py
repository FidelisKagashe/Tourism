from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile, TravelDocument, UserActivityLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser model."""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'nationality', 'is_active', 'date_joined']
    list_filter = ['role', 'nationality', 'is_active', 'email_verified', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Tourism Information', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'gender', 'nationality')
        }),
        ('Profile Information', {
            'fields': ('profile_picture', 'bio', 'preferred_language')
        }),
        ('Travel Preferences', {
            'fields': ('dietary_requirements', 'accessibility_needs', 'travel_experience_level', 'preferred_accommodation_type')
        }),
        ('Verification Status', {
            'fields': ('email_verified', 'phone_verified')
        }),
        ('Communication Preferences', {
            'fields': ('newsletter_subscription', 'marketing_emails')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Tourism Information', {
            'fields': ('role', 'phone_number', 'nationality')
        }),
    )
    
    readonly_fields = ['last_active', 'created_at', 'updated_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""
    
    list_display = ['user', 'emergency_contact_name', 'has_travel_insurance', 'created_at']
    search_fields = ['user__username', 'user__email', 'emergency_contact_name']
    list_filter = ['has_travel_insurance', 'created_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Travel Documents', {
            'fields': ('passport_number', 'passport_expiry', 'passport_issuing_country')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions', 'medications', 'allergies')
        }),
        ('Travel Insurance', {
            'fields': ('has_travel_insurance', 'insurance_provider', 'insurance_policy_number')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TravelDocument)
class TravelDocumentAdmin(admin.ModelAdmin):
    """Admin for TravelDocument model."""
    
    list_display = ['user', 'document_type', 'document_name', 'verified', 'expiry_date', 'created_at']
    list_filter = ['document_type', 'verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'document_name']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('user', 'document_type', 'document_name', 'document_file')
        }),
        ('Verification', {
            'fields': ('verified', 'expiry_date')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin for UserActivityLog model."""
    
    list_display = ['user', 'action_type', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['user', 'action_type', 'description', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False