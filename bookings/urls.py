from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/<slug:tour_slug>/', views.create_booking, name='create_booking'),
    path('<str:booking_reference>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<str:booking_reference>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('api/availability/<int:tour_id>/', views.get_tour_availability, name='tour_availability'),
]