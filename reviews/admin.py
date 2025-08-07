from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewImage, ReviewHelpful

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model."""
    
    list_display = [
        'user', 'review_type', 'get_subject', 'rating', 'is_verified',
        'is_approved', 'helpful_votes', 'created_at'
    ]
    list_filter = ['review_type', 'rating', 'is_verified', 'is_approved', 'travel_type', 'created_at']
    search_fields = ['user__email', 'title', 'content']
    readonly_fields = ['helpful_votes', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'review_type', 'tour_package', 'national_park')
        }),
        ('Review Content', {
            'fields': ('title', 'content', 'rating')
        }),
        ('Additional Ratings', {
            'fields': ('value_for_money', 'service_quality', 'cleanliness')
        }),
        ('Travel Information', {
            'fields': ('travel_date', 'travel_type')
        }),
        ('Status', {
            'fields': ('is_verified', 'verified_purchase', 'is_approved', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('helpful_votes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_subject(self, obj):
        if obj.tour_package:
            return obj.tour_package.title
        elif obj.national_park:
            return obj.national_park.name
        return "General Review"
    get_subject.short_description = 'Subject'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tour_package', 'national_park')

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    """Admin for ReviewImage model."""
    
    list_display = ['review', 'caption', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__title', 'caption']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review')

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    """Admin for ReviewHelpful model."""
    
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__title', 'user__email']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review', 'user')