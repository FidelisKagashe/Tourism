from django.contrib import admin
from .models import ContactMessage, Newsletter, SiteSettings, HistoricalSite
from parks.models import NationalPark, Destination, Wildlife
from tours.models import TourPackage, TourGuide
from reviews.models import Review
from bookings.models import Booking

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin for ContactMessage model."""
    
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    actions = [mark_as_read]

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin for Newsletter model."""
    
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin for SiteSettings model."""
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(HistoricalSite)
class HistoricalSiteAdmin(admin.ModelAdmin):
    """Admin for HistoricalSite model."""
    
    list_display = ['name', 'site_type', 'location', 'region', 'featured', 'is_active', 'created_at']
    list_filter = ['site_type', 'region', 'featured', 'is_active', 'created_at']
    search_fields = ['name', 'location', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'site_type', 'location', 'region')
        }),
        ('Content', {
            'fields': ('description', 'short_description', 'historical_significance')
        }),
        ('Geographic Information', {
            'fields': ('latitude', 'longitude')
        }),
        ('Visitor Information', {
            'fields': ('visiting_hours', 'entry_fee', 'best_time_to_visit')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# Enhanced admin for better content management
class NationalParkInline(admin.TabularInline):
    model = NationalPark
    extra = 0
    fields = ['name', 'region', 'is_active', 'featured']
    readonly_fields = ['name']

class TourPackageInline(admin.TabularInline):
    model = TourPackage
    extra = 0
    fields = ['title', 'category', 'is_active', 'is_featured']
    readonly_fields = ['title']

admin.site.site_header = "Safari & Bush Retreats Admin"
admin.site.site_title = "Safari & Bush Retreats Portal"
admin.site.index_title = "Welcome to Safari & Bush Retreats Administration"

# Register additional models for homepage content management
#admin.site.register(NationalPark)
# admin.site.register(Destination)
# admin.site.register(Wildlife)
# admin.site.register(TourPackage)
# admin.site.register(TourGuide)
# admin.site.register(Review)
# admin.site.register(Booking)