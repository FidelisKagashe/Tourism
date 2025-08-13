from django.contrib import admin
from .models import NationalPark, ParkImage, Destination, Wildlife, ParkFacility

@admin.register(NationalPark)
class NationalParkAdmin(admin.ModelAdmin):
    """Admin for NationalPark model."""
    
    list_display = ['name', 'park_type', 'region', 'area_km2', 'established_year', 'featured', 'is_active']
    list_filter = ['park_type', 'region', 'featured', 'is_active', 'difficulty_level']
    search_fields = ['name', 'location', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'park_type', 'location', 'region')
        }),
        ('Geographic Information', {
            'fields': ('area_km2', 'latitude', 'longitude', 'elevation_min', 'elevation_max')
        }),
        ('Park Details', {
            'fields': ('established_year', 'description', 'short_description', 'main_attractions')
        }),
        ('Visitor Information', {
            'fields': ('best_time_to_visit', 'recommended_duration', 'difficulty_level', 'accessibility_info')
        }),
        ('Entry Fees', {
            'fields': ('entry_fee_citizen', 'entry_fee_resident', 'entry_fee_non_resident')
        }),
        ('Facilities', {
            'fields': ('accommodation_available', 'camping_allowed', 'guided_tours_available', 'restaurant_facilities')
        }),
        ('Media & SEO', {
            'fields': ('main_image', 'meta_title', 'meta_description')
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
    )
    
    actions = ['make_featured', 'remove_featured', 'activate', 'deactivate']
    
    def make_featured(self, request, queryset):
        queryset.update(featured=True)
    make_featured.short_description = "Mark selected parks as featured"
    
    def remove_featured(self, request, queryset):
        queryset.update(featured=False)
    remove_featured.short_description = "Remove featured status"
    
    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = "Activate selected parks"
    
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = "Deactivate selected parks"

@admin.register(ParkImage)
class ParkImageAdmin(admin.ModelAdmin):
    """Admin for ParkImage model."""
    
    list_display = ['park', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['park__name', 'caption']
    list_editable = ['order', 'is_featured']

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    """Admin for Destination model."""
    
    list_display = ['name', 'destination_type', 'park', 'featured', 'is_active', 'created_at']
    list_filter = ['destination_type', 'park', 'featured', 'is_active', 'difficulty_level']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'park', 'destination_type')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'elevation')
        }),
        ('Content', {
            'fields': ('description', 'short_description', 'activities', 'best_time_to_visit')
        }),
        ('Access Information', {
            'fields': ('accessibility', 'walking_distance_from_road', 'difficulty_level')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
    )

@admin.register(Wildlife)
class WildlifeAdmin(admin.ModelAdmin):
    """Admin for Wildlife model."""
    
    list_display = ['common_name', 'scientific_name', 'category', 'conservation_status', 'is_big_five', 'is_endemic', 'is_active']
    list_filter = ['category', 'conservation_status', 'is_big_five', 'is_endemic', 'is_active']
    search_fields = ['common_name', 'scientific_name', 'description']
    filter_horizontal = ['parks']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('common_name', 'scientific_name', 'category', 'conservation_status')
        }),
        ('Description', {
            'fields': ('description', 'physical_characteristics', 'habitat', 'diet', 'behavior')
        }),
        ('Location Information', {
            'fields': ('parks', 'best_viewing_times', 'best_viewing_locations')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('Special Status', {
            'fields': ('is_big_five', 'is_endemic', 'is_active')
        }),
    )
    
    actions = ['mark_big_five', 'unmark_big_five', 'mark_endemic', 'unmark_endemic']
    
    def mark_big_five(self, request, queryset):
        queryset.update(is_big_five=True)
    mark_big_five.short_description = "Mark as Big Five"
    
    def unmark_big_five(self, request, queryset):
        queryset.update(is_big_five=False)
    unmark_big_five.short_description = "Remove Big Five status"

@admin.register(ParkFacility)
class ParkFacilityAdmin(admin.ModelAdmin):
    """Admin for ParkFacility model."""
    
    list_display = ['park', 'facility_type', 'name', 'is_operational', 'capacity']
    list_filter = ['facility_type', 'is_operational', 'park']
    search_fields = ['name', 'park__name']
    readonly_fields = ['created_at', 'updated_at']