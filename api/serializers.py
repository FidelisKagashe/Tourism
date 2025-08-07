from rest_framework import serializers
from parks.models import NationalPark
from tours.models import TourPackage
from bookings.models import Booking
from reviews.models import Review

class NationalParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalPark
        fields = [
            'id', 'name', 'slug', 'park_type', 'location', 'region',
            'area_km2', 'established_year', 'description', 'short_description',
            'main_attractions', 'best_time_to_visit', 'entry_fee_non_resident',
            'main_image', 'featured', 'created_at'
        ]

class TourPackageSerializer(serializers.ModelSerializer):
    parks_visited = NationalParkSerializer(many=True, read_only=True)
    
    class Meta:
        model = TourPackage
        fields = [
            'id', 'title', 'slug', 'category', 'duration_days', 'duration_nights',
            'difficulty_level', 'description', 'short_description', 'highlights',
            'price_budget', 'price_standard', 'price_luxury', 'parks_visited',
            'accommodation_type', 'main_image', 'is_featured', 'average_rating',
            'total_reviews', 'created_at'
        ]

class BookingSerializer(serializers.ModelSerializer):
    tour_package = TourPackageSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_reference', 'tour_package', 'number_of_participants',
            'accommodation_type', 'total_price', 'currency', 'booking_status',
            'payment_status', 'created_at'
        ]
        read_only_fields = ['booking_reference', 'user']

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_display_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user_name', 'title', 'content', 'rating', 'travel_date',
            'travel_type', 'is_verified', 'created_at'
        ]
        read_only_fields = ['user']