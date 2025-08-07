from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django_countries.fields import CountryField

class NationalPark(models.Model):
    """Model representing Tanzania's National Parks and Game Reserves."""
    
    PARK_TYPES = [
        ('national_park', 'National Park'),
        ('game_reserve', 'Game Reserve'),
        ('conservation_area', 'Conservation Area'),
        ('marine_park', 'Marine Park'),
        ('forest_reserve', 'Forest Reserve'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
        ('extreme', 'Extreme'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    park_type = models.CharField(max_length=20, choices=PARK_TYPES, default='national_park')
    location = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    
    # Geographic Information
    area_km2 = models.FloatField(validators=[MinValueValidator(0)])
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    elevation_min = models.IntegerField(blank=True, null=True, help_text="Minimum elevation in meters")
    elevation_max = models.IntegerField(blank=True, null=True, help_text="Maximum elevation in meters")
    
    # Park Details
    established_year = models.IntegerField()
    description = models.TextField()
    short_description = models.TextField(max_length=300)
    
    # Wildlife and Features
    main_attractions = models.TextField(help_text="Main attractions and highlights")
    wildlife_species = models.TextField(help_text="Key wildlife species found in the park")
    vegetation_types = models.TextField(blank=True)
    geological_features = models.TextField(blank=True)
    
    # Visitor Information
    best_time_to_visit = models.TextField()
    recommended_duration = models.CharField(max_length=100, blank=True)
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_LEVELS, default='easy')
    accessibility_info = models.TextField(blank=True)
    
    # Entry Fees (in USD)
    entry_fee_citizen = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entry_fee_resident = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entry_fee_non_resident = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Park Facilities
    accommodation_available = models.BooleanField(default=False)
    camping_allowed = models.BooleanField(default=False)
    guided_tours_available = models.BooleanField(default=True)
    restaurant_facilities = models.BooleanField(default=False)
    
    # Images
    main_image = models.ImageField(upload_to='parks/main/', blank=True, null=True)
    
    # SEO and Meta
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parks_nationalpark'
        verbose_name = 'National Park'
        verbose_name_plural = 'National Parks'
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('parks:park_detail', kwargs={'slug': self.slug})
    
    def get_main_image_url(self):
        """Return main image URL or default image."""
        if self.main_image:
            return self.main_image.url
        return '/static/images/default-park.jpg'

class ParkImage(models.Model):
    """Additional images for national parks."""
    park = models.ForeignKey(NationalPark, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='parks/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'parks_parkimage'
        verbose_name = 'Park Image'
        verbose_name_plural = 'Park Images'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.park.name} - Image {self.order}"

class Destination(models.Model):
    """Destinations within or related to national parks."""
    
    DESTINATION_TYPES = [
        ('wildlife_area', 'Wildlife Area'),
        ('viewpoint', 'Viewpoint'),
        ('waterfall', 'Waterfall'),
        ('lake', 'Lake'),
        ('mountain', 'Mountain'),
        ('crater', 'Crater'),
        ('hot_spring', 'Hot Spring'),
        ('archaeological_site', 'Archaeological Site'),
        ('cultural_site', 'Cultural Site'),
        ('beach', 'Beach'),
        ('island', 'Island'),
        ('village', 'Village'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    park = models.ForeignKey(NationalPark, on_delete=models.CASCADE, related_name='destinations', blank=True, null=True)
    destination_type = models.CharField(max_length=20, choices=DESTINATION_TYPES)
    
    # Geographic Information
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    elevation = models.IntegerField(blank=True, null=True, help_text="Elevation in meters")
    
    # Destination Details
    description = models.TextField()
    short_description = models.TextField(max_length=300)
    activities = models.TextField(blank=True, help_text="Activities available at this destination")
    best_time_to_visit = models.TextField(blank=True)
    
    # Access Information
    accessibility = models.TextField(blank=True)
    walking_distance_from_road = models.CharField(max_length=100, blank=True)
    difficulty_level = models.CharField(max_length=15, choices=NationalPark.DIFFICULTY_LEVELS, default='easy')
    
    # Images
    main_image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parks_destination'
        verbose_name = 'Destination'
        verbose_name_plural = 'Destinations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.park.name if self.park else 'General'})"
    
    def get_absolute_url(self):
        return reverse('parks:destination_detail', kwargs={'slug': self.slug})

class Wildlife(models.Model):
    """Wildlife species found in Tanzania's parks."""
    
    CONSERVATION_STATUS = [
        ('LC', 'Least Concern'),
        ('NT', 'Near Threatened'),
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
        ('EW', 'Extinct in the Wild'),
        ('EX', 'Extinct'),
    ]
    
    WILDLIFE_CATEGORIES = [
        ('mammal', 'Mammal'),
        ('bird', 'Bird'),
        ('reptile', 'Reptile'),
        ('amphibian', 'Amphibian'),
        ('fish', 'Fish'),
        ('insect', 'Insect'),
        ('arachnid', 'Arachnid'),
    ]
    
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=15, choices=WILDLIFE_CATEGORIES)
    conservation_status = models.CharField(max_length=2, choices=CONSERVATION_STATUS, default='LC')
    
    description = models.TextField()
    physical_characteristics = models.TextField(blank=True)
    habitat = models.TextField(blank=True)
    diet = models.TextField(blank=True)
    behavior = models.TextField(blank=True)
    
    # Location Information
    parks = models.ManyToManyField(NationalPark, related_name='wildlife_set')
    best_viewing_times = models.TextField(blank=True)
    best_viewing_locations = models.TextField(blank=True)
    
    # Images
    main_image = models.ImageField(upload_to='wildlife/', blank=True, null=True)
    
    # Big Five indicator
    is_big_five = models.BooleanField(default=False)
    is_endemic = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parks_wildlife'
        verbose_name = 'Wildlife Species'
        verbose_name_plural = 'Wildlife Species'
        ordering = ['common_name']
    
    def __str__(self):
        return self.common_name

class ParkFacility(models.Model):
    """Facilities available in national parks."""
    
    FACILITY_TYPES = [
        ('accommodation', 'Accommodation'),
        ('restaurant', 'Restaurant'),
        ('camping', 'Camping Site'),
        ('visitor_center', 'Visitor Center'),
        ('shop', 'Gift Shop'),
        ('medical', 'Medical Facility'),
        ('fuel_station', 'Fuel Station'),
        ('parking', 'Parking Area'),
        ('viewpoint', 'Viewpoint'),
        ('picnic_area', 'Picnic Area'),
        ('restroom', 'Restroom'),
        ('research_station', 'Research Station'),
    ]
    
    park = models.ForeignKey(NationalPark, on_delete=models.CASCADE, related_name='facilities')
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Location within park
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    
    # Operational Information
    is_operational = models.BooleanField(default=True)
    operating_hours = models.CharField(max_length=100, blank=True)
    contact_info = models.CharField(max_length=200, blank=True)
    
    # Capacity and Features
    capacity = models.IntegerField(blank=True, null=True)
    features = models.TextField(blank=True, help_text="Special features or amenities")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parks_parkfacility'
        verbose_name = 'Park Facility'
        verbose_name_plural = 'Park Facilities'
        ordering = ['facility_type', 'name']
    
    def __str__(self):
        return f"{self.park.name} - {self.name}"