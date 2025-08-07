from django.contrib import admin
from .models import PaymentGateway, Transaction, CurrencyExchangeRate, PaymentMethod

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    """Admin for PaymentGateway model."""
    
    list_display = ['name', 'gateway_type', 'is_active', 'is_test_mode', 'created_at']
    list_filter = ['gateway_type', 'is_active', 'is_test_mode']
    search_fields = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'gateway_type', 'is_active', 'is_test_mode')
        }),
        ('Configuration', {
            'fields': ('api_key', 'secret_key', 'webhook_url', 'supported_currencies')
        }),
        ('Fees', {
            'fields': ('fixed_fee', 'percentage_fee')
        }),
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for Transaction model."""
    
    list_display = [
        'transaction_id', 'booking', 'user', 'amount', 'currency',
        'status', 'payment_gateway', 'created_at'
    ]
    list_filter = ['status', 'transaction_type', 'currency', 'payment_gateway', 'created_at']
    search_fields = ['transaction_id', 'booking__booking_reference', 'user__email']
    readonly_fields = ['transaction_id', 'created_at', 'processed_at', 'completed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'user', 'payment_gateway')

@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    """Admin for CurrencyExchangeRate model."""
    
    list_display = ['base_currency', 'target_currency', 'rate', 'updated_at']
    list_filter = ['base_currency', 'target_currency']
    search_fields = ['base_currency', 'target_currency']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin for PaymentMethod model."""
    
    list_display = ['user', 'method_type', 'card_last_four', 'is_default', 'is_active', 'created_at']
    list_filter = ['method_type', 'is_default', 'is_active']
    search_fields = ['user__email', 'card_last_four']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')