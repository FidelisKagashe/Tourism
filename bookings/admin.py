from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingParticipant, BookingPayment, BookingExtra

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin for Booking model."""
    
    list_display = [
        'booking_reference', 'user', 'tour_package', 'number_of_participants',
        'total_price', 'booking_status', 'payment_status', 'created_at'
    ]
    list_filter = ['booking_status', 'payment_status', 'accommodation_type', 'created_at']
    search_fields = ['booking_reference', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'tour_package', 'tour_availability')
        }),
        ('Booking Details', {
            'fields': ('number_of_participants', 'accommodation_type', 'special_requirements', 'dietary_requirements')
        }),
        ('Pricing', {
            'fields': ('base_price', 'total_price', 'currency')
        }),
        ('Status', {
            'fields': ('booking_status', 'payment_status')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tour_package')

@admin.register(BookingParticipant)
class BookingParticipantAdmin(admin.ModelAdmin):
    """Admin for BookingParticipant model."""
    
    list_display = ['booking', 'first_name', 'last_name', 'nationality', 'date_of_birth']
    list_filter = ['nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'booking__booking_reference']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking')

@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    """Admin for BookingPayment model."""
    
    list_display = [
        'payment_reference', 'booking', 'payment_method', 'amount',
        'currency', 'status', 'created_at'
    ]
    list_filter = ['payment_method', 'status', 'currency', 'created_at']
    search_fields = ['payment_reference', 'booking__booking_reference', 'gateway_transaction_id']
    readonly_fields = ['payment_reference', 'created_at', 'processed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking')

@admin.register(BookingExtra)
class BookingExtraAdmin(admin.ModelAdmin):
    """Admin for BookingExtra model."""
    
    list_display = ['booking', 'extra_name', 'quantity', 'unit_price', 'total_price']
    search_fields = ['booking__booking_reference', 'extra_name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking')