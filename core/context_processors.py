from django.conf import settings
from .models import SiteSettings

def global_context(request):
    """Global context processor."""
    try:
        site_settings = SiteSettings.objects.first()
    except:
        site_settings = None
    
    return {
        'site_settings': site_settings,
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Tanzania Safari Adventures'),
        'SUPPORTED_CURRENCIES': getattr(settings, 'SUPPORTED_CURRENCIES', ['USD', 'EUR', 'TZS']),
        'DEFAULT_CURRENCY': getattr(settings, 'DEFAULT_CURRENCY', 'USD'),
    }