from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from tours.models import TourPackage, TourAvailability
from decimal import Decimal

User = get_user_model()

class Booking(models.Model):
    """Main booking model for tour packages."""
    
    BOOKING_STATUS = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Payment Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Payment Failed'),
    ]
    
    # Basic Information
    booking_reference = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='bookings')
    tour_availability = models.ForeignKey(TourAvailability, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking Details
    number_of_participants = models.IntegerField(validators=[MinValueValidator(1)])
    accommodation_type = models.CharField(
        max_length=20,
        choices=[
            ('budget', 'Budget'),
            ('standard', 'Standard'),
            ('luxury', 'Luxury')
        ],
        default='standard'
    )
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    booking_status = models.CharField(max_length=15, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='pending')
    
    # Special Requirements
    special_requirements = models.TextField(blank=True)
    dietary_requirements = models.TextField(blank=True)
    
    # Contact Information
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'bookings_booking'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_reference} - {self.user.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('bookings:booking_detail', kwargs={'booking_reference': self.booking_reference})
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import uuid
            self.booking_reference = f"TZ{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class BookingParticipant(models.Model):
    """Individual participants in a booking."""
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='participants')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=50)
    passport_number = models.CharField(max_length=20, blank=True)
    dietary_requirements = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings_bookingparticipant'
        verbose_name = 'Booking Participant'
        verbose_name_plural = 'Booking Participants'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class BookingPayment(models.Model):
    """Payment records for bookings."""
    
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_reference = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='pending')
    
    # Payment gateway details
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'bookings_bookingpayment'
        verbose_name = 'Booking Payment'
        verbose_name_plural = 'Booking Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_reference} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.payment_reference:
            import uuid
            self.payment_reference = f"PAY{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

class BookingExtra(models.Model):
    """Additional services/extras added to bookings."""
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='extras')
    extra_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings_bookingextra'
        verbose_name = 'Booking Extra'
        verbose_name_plural = 'Booking Extras'
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.extra_name}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)