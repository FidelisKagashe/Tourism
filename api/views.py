from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from parks.models import NationalPark
from tours.models import TourPackage
from bookings.models import Booking
from reviews.models import Review
from .serializers import (
    NationalParkSerializer, TourPackageSerializer,
    BookingSerializer, ReviewSerializer
)

class NationalParkViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for National Parks."""
    queryset = NationalPark.objects.filter(is_active=True)
    serializer_class = NationalParkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['park_type', 'region', 'featured']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'established_year', 'area_km2']
    ordering = ['name']

class TourPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for Tour Packages."""
    queryset = TourPackage.objects.filter(is_active=True)
    serializer_class = TourPackageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty_level', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'duration_days', 'price_budget', 'average_rating']
    ordering = ['-is_featured', '-created_at']

class BookingViewSet(viewsets.ModelViewSet):
    """API viewset for Bookings."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking_status', 'payment_status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    """API viewset for Reviews."""
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'review_type', 'is_verified']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Review.objects.filter(is_approved=True)
        return Review.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)