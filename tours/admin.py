from django.contrib import admin
from .models import TourGuide, TourPackage, TourItineraryDay, TourImage, TourAvailability, TourPackageExtra

@admin.register(TourGuide)
class TourGuideAdmin(admin.ModelAdmin):
    """Admin for TourGuide model."""
    
    list_display = ['get_full_name', 'license_number', 'certification_level', 'years_of_experience', 'average_rating', 'is_available']
    list_filter = ['certification_level', 'is_available', 'languages']
    search_fields = ['user__first_name', 'user__last_name', 'license_number', 'specializations']
    filter_horizontal = ['parks_covered']
    readonly_fields = ['average_rating', 'total_reviews', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('license_number', 'certification_level', 'years_of_experience')
        }),
        ('Languages & Specializations', {
            'fields': ('languages', 'specializations', 'parks_covered')
        }),
        ('Professional Details', {
            'fields': ('bio', 'qualifications', 'certifications')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'emergency_contact')
        }),
        ('Media', {
            'fields': ('profile_photo',)
        }),
        ('Availability & Pricing', {
            'fields': ('is_available', 'max_group_size', 'daily_rate_usd')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_reviews')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    """Admin for TourPackage model."""
    
    list_display = ['title', 'category', 'duration_days', 'difficulty_level', 'is_featured', 'is_popular', 'average_rating', 'is_active']
    list_filter = ['category', 'difficulty_level', 'is_featured', 'is_popular', 'is_active', 'accommodation_type']
    search_fields = ['title', 'description', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['parks_visited']
    readonly_fields = ['total_bookings', 'average_rating', 'total_reviews', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'category')
        }),
        ('Tour Details', {
            'fields': ('duration_days', 'duration_nights', 'difficulty_level')
        }),
        ('Group Information', {
            'fields': ('min_participants', 'max_participants', 'min_age', 'max_age')
        }),
        ('Descriptions', {
            'fields': ('description', 'short_description', 'highlights', 'detailed_itinerary')
        }),
        ('Inclusions & Exclusions', {
            'fields': ('inclusions', 'exclusions')
        }),
        ('Pricing', {
            'fields': ('price_budget', 'price_standard', 'price_luxury', 'single_supplement_budget', 'single_supplement_standard', 'single_supplement_luxury')
        }),
        ('Parks & Locations', {
            'fields': ('parks_visited',)
        }),
        ('Accommodation & Transport', {
            'fields': ('accommodation_type', 'accommodation_details', 'transportation_details')
        }),
        ('Availability', {
            'fields': ('available_year_round', 'best_months')
        }),
        ('Requirements', {
            'fields': ('fitness_requirements', 'equipment_needed', 'vaccination_requirements', 'visa_requirements')
        }),
        ('Media & SEO', {
            'fields': ('main_image', 'meta_title', 'meta_description')
        }),
        ('Status & Features', {
            'fields': ('is_active', 'is_featured', 'is_popular')
        }),
        ('Statistics', {
            'fields': ('total_bookings', 'average_rating', 'total_reviews')
        }),
    )
    
    actions = ['make_featured', 'remove_featured', 'make_popular', 'remove_popular']
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark as featured"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
    remove_featured.short_description = "Remove featured status"

class TourItineraryDayInline(admin.TabularInline):
    model = TourItineraryDay
    extra = 1
    fields = ['day_number', 'title', 'description', 'overnight_location']

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1
    fields = ['image', 'caption', 'is_featured', 'order']

class TourAvailabilityInline(admin.TabularInline):
    model = TourAvailability
    extra = 1
    fields = ['start_date', 'end_date', 'max_participants', 'assigned_guide', 'is_available']

class TourPackageExtraInline(admin.TabularInline):
    model = TourPackageExtra
    extra = 1
    fields = ['extra_type', 'name', 'price_usd', 'is_available']

# Add inlines to TourPackageAdmin
TourPackageAdmin.inlines = [TourItineraryDayInline, TourImageInline, TourAvailabilityInline, TourPackageExtraInline]

@admin.register(TourItineraryDay)
class TourItineraryDayAdmin(admin.ModelAdmin):
    """Admin for TourItineraryDay model."""
    
    list_display = ['tour_package', 'day_number', 'title', 'overnight_location']
    list_filter = ['tour_package']
    search_fields = ['title', 'description', 'tour_package__title']
    ordering = ['tour_package', 'day_number']

@admin.register(TourAvailability)
class TourAvailabilityAdmin(admin.ModelAdmin):
    """Admin for TourAvailability model."""
    
    list_display = ['tour_package', 'start_date', 'end_date', 'max_participants', 'booked_participants', 'available_spots', 'assigned_guide', 'is_available']
    list_filter = ['is_available', 'start_date', 'assigned_guide']
    search_fields = ['tour_package__title']
    readonly_fields = ['available_spots', 'created_at', 'updated_at']
    
    def available_spots(self, obj):
        # If obj is None (very rarely) or property can't be computed yet, show blank.
        if obj is None:
            return ''

        # Preferred: use the model property if it already returns a safe value (None or int)
        val = getattr(obj, 'available_spots', None)
        if val is not None:
            return val

        # Fallback: compute safely from fields (treat None booked as 0; if max is None -> blank)
        max_p = getattr(obj, 'max_participants', None)
        if max_p is None:
            return ''

        booked = getattr(obj, 'booked_participants', 0) or 0
        try:
            return max(0, int(max_p) - int(booked))
        except (TypeError, ValueError):
            return ''

    available_spots.short_description = 'Available Spots'
