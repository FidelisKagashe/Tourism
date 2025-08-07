from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import CustomUser, UserProfile, UserActivityLog

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when CustomUser is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when CustomUser is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity."""
    UserActivityLog.objects.create(
        user=user,
        action_type='login',
        description=f'User logged in',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity."""
    if user:
        UserActivityLog.objects.create(
            user=user,
            action_type='logout',
            description=f'User logged out',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip