from decimal import Decimal

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch

from .models import Booking, BookingParticipant, BookingPayment, BookingExtra


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin for Booking model."""
    
    list_display = [
        'booking_reference', 'user', 'tour_package', 'number_of_participants',
        'total_price', 'booking_status', 'payment_status', 'created_at'
    ]
    # use related lookup for payment status (payments is the related_name on BookingPayment)
    list_filter = ['booking_status', 'payments__status', 'accommodation_type', 'created_at']
    search_fields = ['booking_reference', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at', 'total_price']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'tour_package', 'tour_availability')
        }),
        ('Booking Details', {
            'fields': ('number_of_participants', 'accommodation_type', 'special_requirements', 'dietary_requirements')
        }),
        # keep only total_price here (base_price/currency are not present on the model)
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Status', {
            'fields': ('booking_status',)  # payment_status is not a model field; use payments for real records
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at')
        }),
    )
    
    def get_queryset(self, request):
        # select_related for FK fields and prefetch extras and payments to avoid N+1 when computing totals/status
        qs = super().get_queryset(request).select_related('user', 'tour_package', 'tour_availability')
        qs = qs.prefetch_related(
            Prefetch('extras', queryset=BookingExtra.objects.all()),
            Prefetch('payments', queryset=BookingPayment.objects.order_by('-created_at'))
        )
        return qs

    def total_price(self, obj):
        """
        Compute total price for display in admin:
        - sum of extras.total_price (BookingExtra.total_price is maintained in model.save)
        - plus tour package or base price * number_of_participants if available
        This method is defensive: it works even if `base_price` / `currency` fields don't exist on Booking.
        """
        total = Decimal('0.00')

        # extras
        try:
            for e in obj.extras.all():
                # BookingExtra sets total_price on save; fall back to quantity * unit_price if needed
                try:
                    total += Decimal(e.total_price)
                except Exception:
                    total += Decimal(e.quantity) * Decimal(e.unit_price)
        except Exception:
            pass

        # base price from booking (if present) or from related tour_package (common pattern)
        base_total = Decimal('0.00')
        try:
            base_price = getattr(obj, 'base_price', None)
            if base_price is not None:
                base_total = Decimal(base_price) * Decimal(obj.number_of_participants)
            else:
                tour = getattr(obj, 'tour_package', None)
                if tour is not None:
                    tour_price = getattr(tour, 'price', None) or getattr(tour, 'base_price', None)
                    if tour_price is not None:
                        base_total = Decimal(tour_price) * Decimal(obj.number_of_participants)
        except Exception:
            # be defensive; if anything goes wrong, just leave base_total as 0
            base_total = Decimal('0.00')

        total += base_total

        # determine currency for display; booking doesn't have currency field in your model, so default to USD
        currency = getattr(obj, 'currency', None) or 'USD'
        # format with two decimals
        try:
            return f"{total:.2f} {currency}"
        except Exception:
            return str(total)

    total_price.short_description = 'Total price'

    def payment_status(self, obj):
        """
        Show the latest payment status for this booking (if any payments exist).
        Falls back to 'No payment' when no payment records exist.
        """
        latest = None
        try:
            latest = obj.payments.order_by('-created_at').first()
        except Exception:
            # defensive: if related manager missing or other error, return unknown
            latest = None

        if latest:
            # use get_FOO_display when available for readable label
            try:
                return latest.get_status_display()
            except Exception:
                return getattr(latest, 'status', str(latest))
        return 'No payment'

    payment_status.short_description = 'Payment status'


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
