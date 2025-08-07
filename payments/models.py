from django.db import models
from django.contrib.auth import get_user_model
from bookings.models import Booking
from decimal import Decimal

User = get_user_model()

class PaymentGateway(models.Model):
    """Payment gateway configurations."""
    
    GATEWAY_TYPES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('flutterwave', 'Flutterwave'),
    ]
    
    name = models.CharField(max_length=50)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    
    # Configuration
    api_key = models.CharField(max_length=200, blank=True)
    secret_key = models.CharField(max_length=200, blank=True)
    webhook_url = models.URLField(blank=True)
    
    # Supported currencies
    supported_currencies = models.JSONField(default=list)
    
    # Fees
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percentage_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_paymentgateway'
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    """Payment transactions."""
    
    TRANSACTION_TYPES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('partial_refund', 'Partial Refund'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Basic Information
    transaction_id = models.CharField(max_length=50, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1)
    
    # Gateway Information
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_reference = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(max_length=15, choices=TRANSACTION_STATUS, default='pending')
    failure_reason = models.TextField(blank=True)
    
    # Fees
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments_transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TXN{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

class CurrencyExchangeRate(models.Model):
    """Currency exchange rates."""
    
    base_currency = models.CharField(max_length=3, default='USD')
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_currencyexchangerate'
        verbose_name = 'Currency Exchange Rate'
        verbose_name_plural = 'Currency Exchange Rates'
        unique_together = ['base_currency', 'target_currency']
    
    def __str__(self):
        return f"{self.base_currency}/{self.target_currency} - {self.rate}"

class PaymentMethod(models.Model):
    """User saved payment methods."""
    
    METHOD_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_account', 'Bank Account'),
        ('mobile_money', 'Mobile Money'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    
    # Card Information (encrypted)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_expiry_month = models.IntegerField(blank=True, null=True)
    card_expiry_year = models.IntegerField(blank=True, null=True)
    
    # Gateway token
    gateway_token = models.CharField(max_length=200, blank=True)
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments_paymentmethod'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.card_last_four:
            return f"{self.card_brand} ending in {self.card_last_four}"
        return f"{self.method_type}"