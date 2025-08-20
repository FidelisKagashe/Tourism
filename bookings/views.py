# bookings/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction, IntegrityError

from .models import Booking, BookingParticipant
from .forms import QuickBookingForm, SimpleParticipantFormSet
from tours.models import TourPackage, TourAvailability


class BookingListView(LoginRequiredMixin, ListView):
    """List bookings for the logged-in user."""
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            'tour_package', 'tour_availability'
        ).order_by('-created_at')


class BookingDetailView(LoginRequiredMixin, DetailView):
    """Booking detail view by booking_reference."""
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
    """
    Simplified booking flow: minimal fields, optional participant names.
    Payment is assumed to be cash/on-arrival (no gateway).
    Handles availability.available_spots == None (capacity-on-request) safely.
    """
    tour_package = get_object_or_404(TourPackage, slug=tour_slug, is_active=True)

    if request.method == 'POST':
        form = QuickBookingForm(request.POST)
        include_participants = request.POST.get('include_participants') == '1'
        participant_formset = SimpleParticipantFormSet(request.POST) if include_participants else None

        if form.is_valid() and (not include_participants or (participant_formset and participant_formset.is_valid())):
            # Get availability model instance from the form (may be None)
            availability = form.cleaned_data.get('tour_availability')
            # normalize requested participants to int (default 1)
            try:
                num = int(form.cleaned_data.get('number_of_participants') or 1)
                if num < 1:
                    num = 1
            except (TypeError, ValueError):
                num = 1

            # availability.available_spots may be None (meaning "capacity on request")
            avail_spots = None
            if availability is not None:
                avail_spots = getattr(availability, 'available_spots', None)

            # If we have a definite capacity (int), enforce it.
            if avail_spots is not None and isinstance(avail_spots, int) and avail_spots < num:
                messages.error(request, 'Not enough available spots for the selected date. Please choose another date or reduce participants.')
            else:
                # Either avail_spots is None (capacity-on-request) OR enough spots -> proceed
                try:
                    with transaction.atomic():
                        booking = form.save(commit=False)
                        booking.user = request.user
                        booking.tour_package = tour_package
                        # Prefill contact info from user (safe defaults)
                        booking.contact_name = request.user.get_full_name() or request.user.username
                        booking.contact_email = request.user.email or ''
                        # Mark as pending — consistent with your current business flow
                        booking.booking_status = 'pending'
                        booking.save()

                        # Save participants if provided
                        if include_participants and participant_formset:
                            participant_formset.instance = booking
                            participant_formset.save()

                        # Update availability.booked_participants if availability exists.
                        # We attempt to increment booked_participants but guard against DB integrity issues.
                        if availability is not None:
                            try:
                                # booked_participants is expected to be an integer field
                                availability.booked_participants = (availability.booked_participants or 0) + booking.number_of_participants
                                availability.save()
                            except (IntegrityError, TypeError, ValueError):
                                # If updating availability fails (schema mismatch or null constraints),
                                # we swallow the failure (booking is still saved) and notify staff via message.
                                messages.warning(request, 'Booking saved but failed to update availability counters; staff will reconcile this manually.')

                        # If capacity was unspecified, inform the user that capacity will be confirmed.
                        if avail_spots is None:
                            messages.info(request,
                                'Capacity for the selected date is confirmed on request. We accepted your booking request and will confirm availability shortly.')

                        # Fire-and-forget email (non-blocking)
                        send_booking_confirmation_email(booking)

                        messages.success(request, f'Booking received! Reference: {booking.booking_reference}. Our team will contact you shortly.')
                        return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)
                except Exception as exc:
                    # fallback: roll back and show error
                    messages.error(request, f'Could not complete booking: {exc}')
        else:
            # form or formset invalid - show friendly message
            messages.error(request, 'Please correct the errors in the form and try again.')
    else:
        form = QuickBookingForm()
        participant_formset = SimpleParticipantFormSet()

    context = {
        'tour_package': tour_package,
        'form': form,
        'participant_formset': participant_formset,
    }
    return render(request, 'bookings/create_booking.html', context)


@login_required
def create_booking_quick(request, tour_slug):
    """
    One-click reserve endpoint:
    - Reserves for 1 person (or uses number_of_participants posted).
    - If availability.available_spots is None (capacity-on-request), booking is allowed and set to pending.
    """
    tour_package = get_object_or_404(TourPackage, slug=tour_slug, is_active=True)

    if request.method != 'POST':
        raise Http404()

    try:
        num = int(request.POST.get('number_of_participants', 1))
        if num < 1:
            num = 1
    except (TypeError, ValueError):
        num = 1

    availability_id = request.POST.get('availability_id')  # optional
    if availability_id:
        availability = get_object_or_404(TourAvailability, pk=availability_id, tour_package=tour_package, is_available=True)
    else:
        # pick next available
        availability = TourAvailability.objects.filter(tour_package=tour_package, is_available=True).order_by('start_date').first()

    # compute avail_spots safely (None means capacity-on-request)
    avail_spots = None
    if availability is not None:
        avail_spots = getattr(availability, 'available_spots', None)

    if availability is None:
        messages.error(request, 'Could not reserve — no availability found for this tour.')
        return redirect('tours:tour_detail', slug=tour_slug)

    # If definitive capacity exists and it's insufficient, bail out
    if avail_spots is not None and isinstance(avail_spots, int) and avail_spots < num:
        messages.error(request, 'Could not reserve — not enough confirmed capacity for the selected date.')
        return redirect('tours:tour_detail', slug=tour_slug)

    # Proceed to create booking (allowed for avail_spots None -> pending)
    try:
        with transaction.atomic():
            booking = Booking.objects.create(
                user=request.user,
                tour_package=tour_package,
                tour_availability=availability,
                number_of_participants=num,
                accommodation_type='standard',
                contact_name=request.user.get_full_name() or request.user.username,
                contact_email=request.user.email or '',
                contact_phone=getattr(request.user, 'phone_number', '') if hasattr(request.user, 'phone_number') else '',
                booking_status='pending',
            )
            # update availability counters if possible
            try:
                availability.booked_participants = (availability.booked_participants or 0) + booking.number_of_participants
                availability.save()
            except (IntegrityError, TypeError, ValueError):
                messages.warning(request, 'Reservation created but failed to update availability counters; staff will reconcile this manually.')

            send_booking_confirmation_email(booking)
            messages.success(request, f'Quick reservation done. Reference: {booking.booking_reference}')
            return redirect('bookings:booking_detail', booking_reference=booking.booking_reference)
    except Exception as exc:
        messages.error(request, f'Could not complete quick reservation: {exc}')
        return redirect('tours:tour_detail', slug=tour_slug)


@login_required
def cancel_booking(request, booking_reference):
    """Cancel a booking if allowed."""
    booking = get_object_or_404(
        Booking,
        booking_reference=booking_reference,
        user=request.user,
        booking_status__in=['pending', 'confirmed']
    )

    if request.method == 'POST':
        # preserve previous status
        previous_status = booking.booking_status
        booking.booking_status = 'cancelled'
        booking.save()

        # If previously confirmed, free up spots
        if previous_status == 'confirmed' and booking.tour_availability:
            availability = booking.tour_availability
            try:
                availability.booked_participants = max(0, (availability.booked_participants or 0) - booking.number_of_participants)
                availability.save()
            except (IntegrityError, TypeError, ValueError):
                # log/warn in production; user-facing message kept simple
                messages.warning(request, 'Booking cancelled but availability counter could not be updated automatically.')

        messages.success(request, 'Booking cancelled successfully.')
        return redirect('bookings:booking_list')

    return render(request, 'bookings/cancel_booking.html', {'booking': booking})


def get_tour_availability(request, tour_id):
    """AJAX endpoint to get tour availability for a given tour.

    Returns availability entries with a computed 'remaining' key:
    - remaining is int when max_participants is defined,
    - remaining is null when capacity is unspecified (business: capacity on request).
    """
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        avail_qs = TourAvailability.objects.filter(
            tour_package_id=tour_id,
            is_available=True
        )
        if start_date:
            avail_qs = avail_qs.filter(start_date__gte=start_date)

        availabilities = []
        for a in avail_qs.order_by('start_date'):
            # compute remaining in Python so we can return None when max_participants is None
            try:
                if getattr(a, 'max_participants', None) is None:
                    remaining = None
                else:
                    remaining = max(0, (a.max_participants or 0) - (a.booked_participants or 0))
            except Exception:
                remaining = None

            availabilities.append({
                'id': a.id,
                'start_date': a.start_date,
                'end_date': a.end_date,
                'remaining': remaining,
            })

        return JsonResponse({'availabilities': availabilities})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# -----------------------
# Email helper functions
# -----------------------
def send_booking_confirmation_email(booking):
    """Send booking confirmation email (HTML)."""
    try:
        subject = f'Booking Request Received - {booking.booking_reference}'
        html_message = render_to_string('emails/booking_confirmation.html', {'booking': booking})
        send_mail(
            subject=subject,
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.contact_email],
            fail_silently=True,
        )
    except Exception:
        # Don't let email failures block booking flow
        pass


def send_payment_confirmation_email(booking, payment):
    try:
        subject = f'Payment Confirmation - {booking.booking_reference}'
        html_message = render_to_string('emails/payment_confirmation.html', {'booking': booking, 'payment': payment})
        send_mail(subject=subject, message='', html_message=html_message, from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[booking.contact_email], fail_silently=True)
    except Exception:
        pass


def send_cash_payment_confirmation_email(booking, payment):
    try:
        subject = f'Booking Confirmed - Cash Payment - {booking.booking_reference}'
        html_message = render_to_string('emails/cash_payment_confirmation.html', {'booking': booking, 'payment': payment})
        send_mail(subject=subject, message='', html_message=html_message, from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[booking.contact_email], fail_silently=True)
    except Exception:
        pass
