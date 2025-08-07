from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from tours.models import TourPackage
from parks.models import NationalPark

User = get_user_model()

class Review(models.Model):
    """Reviews for tour packages and parks."""
    
    REVIEW_TYPES = [
        ('tour', 'Tour Package Review'),
        ('park', 'National Park Review'),
        ('guide', 'Tour Guide Review'),
    ]
    
    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPES, default='tour')
    
    # Related Objects
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    national_park = models.ForeignKey(NationalPark, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    
    # Review Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Additional Ratings
    value_for_money = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    service_quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    cleanliness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    
    # Travel Information
    travel_date = models.DateField(blank=True, null=True)
    travel_type = models.CharField(
        max_length=20,
        choices=[
            ('solo', 'Solo Travel'),
            ('couple', 'Couple'),
            ('family', 'Family'),
            ('friends', 'Friends'),
            ('business', 'Business'),
        ],
        blank=True
    )
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_purchase = models.BooleanField(default=False)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Interaction
    helpful_votes = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews_review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['user', 'tour_package', 'national_park']
    
    def __str__(self):
        if self.tour_package:
            return f"{self.user.get_display_name()} - {self.tour_package.title}"
        elif self.national_park:
            return f"{self.user.get_display_name()} - {self.national_park.name}"
        return f"{self.user.get_display_name()} - Review"
    
    def get_star_range(self):
        """Return range for template star display."""
        return range(1, 6)
    
    def get_filled_stars(self):
        """Return range of filled stars."""
        return range(1, self.rating + 1)
    
    def get_empty_stars(self):
        """Return range of empty stars."""
        return range(self.rating + 1, 6)

class ReviewImage(models.Model):
    """Images attached to reviews."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reviews_reviewimage'
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.review} - Image {self.order}"

class ReviewHelpful(models.Model):
    """Track helpful votes for reviews."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes_detail')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reviews_reviewhelpful'
        verbose_name = 'Review Helpful Vote'
        verbose_name_plural = 'Review Helpful Votes'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.review}"