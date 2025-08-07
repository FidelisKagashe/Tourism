from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Explicit basenames to avoid automatic lookup issues
router.register(r'parks', views.NationalParkViewSet, basename='park')
router.register(r'tours', views.TourPackageViewSet, basename='tour')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
