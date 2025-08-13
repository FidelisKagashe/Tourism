from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from parks.models import NationalPark
from typing import Optional

User = get_user_model()

class TourGuide(models.Model):
    """Professional tour guides."""
    
    CERTIFICATION_LEVELS = [
        ('basic', 'Basic Certified'),
        ('advanced', 'Advanced Certified'),
        ('specialist', 'Specialist'),
        ('master', 'Master Guide'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('sw', 'Kiswahili'),
        ('fr', 'French'),
        ('de', 'German'),
        ('es', 'Spanish'),
        ('it', 'Italian'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ar', 'Arabic'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guide_profile')
    
    # Professional Information
    license_number = models.CharField(max_length=50, unique=True)
    certification_level = models.CharField(max_length=15, choices=CERTIFICATION_LEVELS)
    years_of_experience = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Languages spoken
    languages = models.JSONField(default=list, help_text="List of languages spoken")
    
    # Specializations
    specializations = models.TextField(help_text="Areas of expertise (wildlife, culture, trekking, etc.)")
    parks_covered = models.ManyToManyField(NationalPark, related_name='guides')
    
    # Professional Details
    bio = models.TextField()
    qualifications = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=100, blank=True)
    
    # Professional Photos
    profile_photo = models.ImageField(upload_to='guides/profiles/', blank=True, null=True)
    
    # Rating and Reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    
    # Availability
    is_available = models.BooleanField(default=True)
    max_group_size = models.IntegerField(default=8)
    
    # Financial Information
    daily_rate_usd = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tours_tourguide'
        verbose_name = 'Tour Guide'
        verbose_name_plural = 'Tour Guides'
        ordering = ['-average_rating', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.certification_level}"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_absolute_url(self):
        return reverse('tours:guide_detail', kwargs={'pk': self.pk})

class TourPackage(models.Model):
    """Tour packages offered by the company."""
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
        ('extreme', 'Extreme'),
    ]
    
    TOUR_CATEGORIES = [
        ('safari', 'Wildlife Safari'),
        ('trekking', 'Mountain Trekking'),
        ('cultural', 'Cultural Experience'),
        ('beach', 'Beach & Marine'),
        ('adventure', 'Adventure'),
        ('photography', 'Photography Tour'),
        ('birding', 'Bird Watching'),
        ('honeymoon', 'Honeymoon Package'),
        ('family', 'Family Safari'),
        ('luxury', 'Luxury Experience'),
    ]
    
    ACCOMMODATION_TYPES = [
        ('camping', 'Camping'),
        ('lodge', 'Safari Lodge'),
        ('hotel', 'Hotel'),
        ('tented_camp', 'Tented Camp'),
        ('luxury_camp', 'Luxury Camp'),
        ('mobile_camp', 'Mobile Camp'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    subtitle = models.CharField(max_length=300, blank=True)
    category = models.CharField(max_length=20, choices=TOUR_CATEGORIES)
    
    # Tour Details
    duration_days = models.IntegerField(validators=[MinValueValidator(1)])
    duration_nights = models.IntegerField(validators=[MinValueValidator(0)])
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_LEVELS)
    
    # Group Information
    min_participants = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_participants = models.IntegerField(default=8, validators=[MinValueValidator(1)])
    min_age = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_age = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    
    # Descriptions
    description = models.TextField()
    short_description = models.TextField(max_length=500)
    highlights = models.JSONField(default=list, help_text="List of tour highlights")
    
    # Itinerary
    detailed_itinerary = models.TextField()
    
    # Inclusions and Exclusions
    inclusions = models.JSONField(default=list, help_text="What's included in the tour")
    exclusions = models.JSONField(default=list, help_text="What's not included")
    
    # Pricing (Base prices in USD)
    price_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_standard = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_luxury = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Single supplement charges
    single_supplement_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    single_supplement_standard = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    single_supplement_luxury = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Parks and Locations
    parks_visited = models.ManyToManyField(NationalPark, related_name='tour_packages')
    
    # Accommodation
    accommodation_type = models.CharField(max_length=20, choices=ACCOMMODATION_TYPES)
    accommodation_details = models.TextField(blank=True)
    
    # Transportation
    transportation_details = models.TextField(blank=True)
    
    # Availability
    available_year_round = models.BooleanField(default=True)
    best_months = models.JSONField(default=list, help_text="Best months to take this tour")
    
    # Requirements and Preparations
    fitness_requirements = models.TextField(blank=True)
    equipment_needed = models.TextField(blank=True)
    vaccination_requirements = models.TextField(blank=True)
    visa_requirements = models.TextField(blank=True)
    
    # Images
    main_image = models.ImageField(upload_to='tours/main/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Status and Features
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    
    # Statistics
    total_bookings = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tours_tourpackage'
        verbose_name = 'Tour Package'
        verbose_name_plural = 'Tour Packages'
        ordering = ['-is_featured', '-is_popular', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('tours:package_detail', kwargs={'slug': self.slug})
    
    def get_duration_display(self):
        """Return formatted duration."""
        if self.duration_nights > 0:
            return f"{self.duration_days} days, {self.duration_nights} nights"
        return f"{self.duration_days} day{'s' if self.duration_days > 1 else ''}"
    
    def get_price_range(self):
        """Return price range for display."""
        prices = [p for p in [self.price_budget, self.price_standard, self.price_luxury] if p is not None]
        if not prices:
            return "Price on request"
        
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return f"${min_price:,.0f}"
        return f"${min_price:,.0f} - ${max_price:,.0f}"

class TourItineraryDay(models.Model):
    """Detailed daily itinerary for tour packages."""
    
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='itinerary_days')
    day_number = models.IntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=200)
    description = models.TextField()
    activities = models.JSONField(default=list, help_text="List of activities for the day")
    
    # Location Information
    overnight_location = models.CharField(max_length=100, blank=True)
    meals_included = models.JSONField(default=list, help_text="Meals included (breakfast, lunch, dinner)")
    
    # Travel Information
    travel_distance = models.CharField(max_length=100, blank=True, help_text="e.g., '120km, 3 hours'")
    travel_method = models.CharField(max_length=100, blank=True, help_text="e.g., 'Safari vehicle', 'Walking'")
    
    # Images
    day_image = models.ImageField(upload_to='tours/itinerary/', blank=True, null=True)
    
    class Meta:
        db_table = 'tours_touritineraryday'
        verbose_name = 'Tour Itinerary Day'
        verbose_name_plural = 'Tour Itinerary Days'
        ordering = ['tour_package', 'day_number']
        unique_together = ['tour_package', 'day_number']
    
    def __str__(self):
        return f"{self.tour_package.title} - Day {self.day_number}: {self.title}"

class TourImage(models.Model):
    """Images for tour packages."""
    
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tours_tourimage'
        verbose_name = 'Tour Image'
        verbose_name_plural = 'Tour Images'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.tour_package.title} - Image {self.order}"

class TourAvailability(models.Model):
    """Track availability and pricing for specific dates."""
    
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='availability')
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Pricing modifiers for seasonal pricing
    price_modifier_budget = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    price_modifier_standard = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    price_modifier_luxury = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    
    # Availability
    max_participants = models.IntegerField()
    booked_participants = models.IntegerField(default=0)
    
    # Guide assignment
    assigned_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Status
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tours_touravailability'
        verbose_name = 'Tour Availability'
        verbose_name_plural = 'Tour Availability'
        ordering = ['start_date']
        unique_together = ['tour_package', 'start_date']
    
    def __str__(self):
        return f"{self.tour_package.title} - {self.start_date}"
    
    @property
    def available_spots(self) -> Optional[int]:
        """
        Return number of available spots as an int, or None if it cannot be computed yet.
        - If max_participants is None we return None (admin will show blank).
        - If booked_participants is None we treat it as 0.
        """
        max_p = self.max_participants
        if max_p is None:
            return None

        booked = self.booked_participants or 0

        try:
            available = int(max_p) - int(booked)
        except (TypeError, ValueError):
            return None

        return max(0, available)

    @property
    def is_fully_booked(self) -> bool:
        """
        Return True if booked_participants >= max_participants.
        If max_participants is not set, consider it NOT fully booked.
        """
        max_p = self.max_participants
        if max_p is None:
            return False
        return (self.booked_participants or 0) >= int(max_p)

class TourPackageExtra(models.Model):
    """Optional extras that can be added to tour packages."""
    
    EXTRA_TYPES = [
        ('accommodation', 'Accommodation Upgrade'),
        ('activity', 'Additional Activity'),
        ('equipment', 'Equipment Rental'),
        ('service', 'Additional Service'),
        ('transport', 'Transport Option'),
        ('meal', 'Meal Option'),
        ('insurance', 'Travel Insurance'),
    ]
    
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='extras')
    extra_type = models.CharField(max_length=20, choices=EXTRA_TYPES)
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Availability
    is_available = models.BooleanField(default=True)
    max_quantity_per_booking = models.IntegerField(default=1)
    
    # Requirements
    requires_advance_booking = models.BooleanField(default=False)
    advance_booking_days = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tours_tourpackageextra'
        verbose_name = 'Tour Package Extra'
        verbose_name_plural = 'Tour Package Extras'
        ordering = ['extra_type', 'name']
    
    def __str__(self):
        return f"{self.tour_package.title} - {self.name}"