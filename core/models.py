from django.db import models
from django.core.validators import EmailValidator
from django.urls import reverse

class ContactMessage(models.Model):
    """Contact form messages."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_contactmessage'
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class Newsletter(models.Model):
    """Newsletter subscriptions."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_newsletter'
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email

class SiteSettings(models.Model):
    """Site-wide settings."""
    site_name = models.CharField(max_length=100, default="Tanzania Safari Adventures")
    site_description = models.TextField(default="Discover Tanzania's wildlife and national parks")
    contact_email = models.EmailField(default="info@tanzaniasafari.com")
    contact_phone = models.CharField(max_length=20, default="+255 123 456 789")
    address = models.TextField(default="Arusha, Tanzania")
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO
    meta_keywords = models.TextField(blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_sitesettings'
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name

class HistoricalSite(models.Model):
    """Historical sites in Tanzania."""
    
    SITE_TYPES = [
        ('archaeological', 'Archaeological Site'),
        ('cultural', 'Cultural Heritage Site'),
        ('colonial', 'Colonial Heritage'),
        ('religious', 'Religious Site'),
        ('museum', 'Museum'),
        ('monument', 'Monument'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    site_type = models.CharField(max_length=20, choices=SITE_TYPES)
    location = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    
    description = models.TextField()
    short_description = models.TextField(max_length=300)
    historical_significance = models.TextField()
    
    # Geographic Information
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    
    # Visitor Information
    visiting_hours = models.CharField(max_length=100, blank=True)
    entry_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    best_time_to_visit = models.TextField(blank=True)
    
    # Images
    main_image = models.ImageField(upload_to='historical_sites/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_historicalsite'
        verbose_name = 'Historical Site'
        verbose_name_plural = 'Historical Sites'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('core:historical_site_detail', kwargs={'slug': self.slug})