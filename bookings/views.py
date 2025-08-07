from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Booking, BookingParticipant, BookingPayment
from .forms import BookingForm, BookingParticipantFormSet, PaymentForm
from tours.models import TourPackage, TourAvailability
import json
from decimal import Decimal

class BookingListView(LoginRequiredMixin, ListView):
    """List user's bookings."""
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            'tour_package', 'tour_availability'
        ).order_by('-created_at')

class BookingDetailView(LoginRequiredMixin, DetailView):
    """Booking detail view."""
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    slug_field = 'booking_reference'
    slug_url_kwarg = 'booking_reference'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            'tour_package', 'tour_availability'
        ).prefetch_related('participants', 'payments', 'extras')

@login_required
def create_booking(request, tour_slug):
    """Create a new booking."""
    tour_package = get_object_or_404(TourPackage, slug=tour_slug, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        participant_formset = BookingParticipantFormSet(request.POST)
        
        if form.is_valid() and participant_formset.is_valid():
            # Create booking
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour_package = tour_package
            booking.contact_name = request.user.get_full_name()
            booking.contact_email = request.user.email
            booking.contact_phone = request.user.phone_number or ''
            
            # Calculate pricing
            accommodation_type = form.cleaned_data['accommodation_type']
            participants = form.cleaned_data['number_of_participants']
            
            if accommodation_type == 'budget':
                base_price = tour_package.price_budget or Decimal('0')
            elif accommodation_type == 'luxury':
                base_price = tour_package.price_luxury or Decimal('0')
            else:
                base_price = tour_package.price_standard or Decimal('0')
            
            booking.base_price = base_price
            booking.total_price = base_price * participants
            booking.save()
            
            # Save participants
            participant_formset.instance = booking
            participant_formset.save()
            
            # Send confirmation email
            send_booking_confirmation_email(booking)
            
            messages.success(request, f'Booking created successfully! Reference: {booking.booking_reference}')
            return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)
    else:
        form = BookingForm()
        participant_formset = BookingParticipantFormSet()
    
    context = {
        'tour_package': tour_package,
        'form': form,
        'participant_formset': participant_formset,
    }
    return render(request, 'bookings/create_booking.html', context)

@login_required
def booking_payment(request, booking_reference):
    """Process booking payment."""
    booking = get_object_or_404(
        Booking, 
        booking_reference=booking_reference, 
        user=request.user,
        booking_status='pending'
    )
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Create payment record
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_price
            payment.currency = booking.currency
            payment.save()
            
            # Simulate payment processing
            if simulate_payment_processing(payment):
                payment.status = 'completed'
                payment.save()
                
                booking.payment_status = 'paid'
                booking.booking_status = 'confirmed'
                booking.save()
                
                # Update tour availability
                availability = booking.tour_availability
                availability.booked_participants += booking.number_of_participants
                availability.save()
                
                # Send confirmation
                send_payment_confirmation_email(booking, payment)
                
                messages.success(request, 'Payment successful! Your booking is confirmed.')
                return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)
            else:
                payment.status = 'failed'
                payment.save()
                messages.error(request, 'Payment failed. Please try again.')
    else:
        form = PaymentForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'bookings/booking_payment.html', context)

def simulate_payment_processing(payment):
    """Simulate payment gateway processing."""
    # In real implementation, this would integrate with actual payment gateway
    import random
    return random.choice([True, True, True, False])  # 75% success rate

def send_booking_confirmation_email(booking):
    """Send booking confirmation email."""
    subject = f'Booking Confirmation - {booking.booking_reference}'
    html_message = render_to_string('emails/booking_confirmation.html', {'booking': booking})
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.contact_email],
        fail_silently=True,
    )

def send_payment_confirmation_email(booking, payment):
    """Send payment confirmation email."""
    subject = f'Payment Confirmation - {booking.booking_reference}'
    html_message = render_to_string('emails/payment_confirmation.html', {
        'booking': booking,
        'payment': payment
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.contact_email],
        fail_silently=True,
    )

@login_required
def cancel_booking(request, booking_reference):
    """Cancel a booking."""
    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user,
        booking_status__in=['pending', 'confirmed']
    )
    
    if request.method == 'POST':
        booking.booking_status = 'cancelled'
        booking.save()
        
        # Update availability
        if booking.booking_status == 'confirmed':
            availability = booking.tour_availability
            availability.booked_participants -= booking.number_of_participants
            availability.save()
        
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('bookings:booking_list')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

def get_tour_availability(request, tour_id):
    """AJAX endpoint to get tour availability."""
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        if start_date:
            availabilities = TourAvailability.objects.filter(
                tour_package_id=tour_id,
                start_date__gte=start_date,
                is_available=True
            ).values('id', 'start_date', 'end_date', 'available_spots')
            
            return JsonResponse({
                'availabilities': list(availabilities)
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)