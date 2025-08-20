# bookings/urls.py
from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # List the user's bookings
    path('', views.BookingListView.as_view(), name='booking_list'),

    # Standard (simplified) booking page.
    # This should point to the simplified `create_booking` view (the fast "shap-shap" flow).
    path('create/<slug:tour_slug>/', views.create_booking, name='create_booking'),

    # Optional: explicit quick / one-click endpoint if you later add a one-click flow.
    # You can remove this if you don't plan to use it.
    path('create/quick/<slug:tour_slug>/', views.create_booking_quick, name='create_booking_quick'),

    # Booking detail & cancel
    path('<str:booking_reference>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<str:booking_reference>/cancel/', views.cancel_booking, name='cancel_booking'),

    # AJAX endpoint for availability used by the form
    path('api/availability/<int:tour_id>/', views.get_tour_availability, name='tour_availability'),
]
