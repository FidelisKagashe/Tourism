from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, F, Value
from django.db.models import ExpressionWrapper, IntegerField
from django.contrib.auth.decorators import login_required
from .models import TourPackage, TourGuide, TourAvailability

def tour_list(request):
    """
    Tour list with filters, search, sorting and pagination.
    Price-related behaviour intentionally removed.
    """
    qs = TourPackage.objects.filter(is_active=True).prefetch_related('parks_visited')

    # sanitize params
    category = (request.GET.get('category') or '').strip()
    difficulty = (request.GET.get('difficulty') or '').strip()
    duration = (request.GET.get('duration') or '').strip()
    search = (request.GET.get('search') or '').strip()
    sort_by = (request.GET.get('sort') or 'featured').strip()

    # Filtering
    if category:
        qs = qs.filter(category=category)

    if difficulty:
        qs = qs.filter(difficulty_level=difficulty)

    if duration:
        if duration == 'short':
            qs = qs.filter(duration_days__lte=3)
        elif duration == 'medium':
            qs = qs.filter(duration_days__range=(4, 7))
        elif duration == 'long':
            qs = qs.filter(duration_days__gte=8)

    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(short_description__icontains=search) |
            Q(highlights__icontains=search)
        )

    # Sorting (validate against allowed options)
    if sort_by == 'duration':
        qs = qs.order_by('duration_days', 'title')
    elif sort_by == 'rating':
        qs = qs.order_by('-average_rating', '-total_reviews', 'title')
    else:
        # featured default: featured -> popular -> newest
        qs = qs.order_by('-is_featured', '-is_popular', '-created_at')

    qs = qs.distinct()

    # Pagination
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Provide choice lists for template selects
    categories = getattr(TourPackage, 'TOUR_CATEGORIES', [])
    difficulties = getattr(TourPackage, 'DIFFICULTY_LEVELS', [])
    sort_options = [
        ('featured', 'Featured'),
        ('duration', 'Duration'),
        ('rating', 'Rating'),
    ]

    context = {
        'page_obj': page_obj,
        'current_category': category,
        'current_difficulty': difficulty,
        'current_duration': duration,
        'current_sort': sort_by,
        'search_query': search,

        'categories': categories,
        'difficulties': difficulties,
        'sort_options': sort_options,
    }
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, slug):
    """Tour package detail view."""
    tour = get_object_or_404(
        TourPackage.objects.select_related().prefetch_related(
            'parks_visited', 'itinerary_days', 'images', 'reviews__user', 'extras'
        ),
        slug=slug,
        is_active=True
    )

    # Annotate a `remaining` column: max_participants - booked_participants.
    # If max_participants is NULL, remaining will be NULL (i.e. unlimited).
    availability_qs = tour.availability.annotate(
        remaining=ExpressionWrapper(
            F('max_participants') - F('booked_participants'),
            output_field=IntegerField()
        )
    )

    # We want availabilities that are:
    #  - is_available=True AND
    #  - (max_participants IS NULL) OR (remaining > 0)
    # This keeps "unlimited" (max_participants NULL) rows and only shows
    # limited rows that have at least one remaining spot.
    availability = (
        availability_qs
        .filter(is_available=True)
        .filter(Q(max_participants__isnull=True) | Q(remaining__gt=0))
        .order_by('start_date')[:10]
    )

    # Get reviews
    reviews = tour.reviews.filter(is_approved=True).select_related('user')[:10]

    # Get related tours
    related_tours = TourPackage.objects.filter(
        category=tour.category,
        is_active=True
    ).exclude(id=tour.id)[:4]

    context = {
        'tour': tour,
        'availability': availability,  # annotated .remaining available on each item
        'reviews': reviews,
        'related_tours': related_tours,
    }
    return render(request, 'tours/tour_detail.html', context)


def guide_list(request):
    """List all tour guides."""
    guides = TourGuide.objects.filter(is_available=True).select_related('user')

    # Filtering
    certification = request.GET.get('certification')
    specialization = request.GET.get('specialization')
    search = request.GET.get('search')

    if certification:
        guides = guides.filter(certification_level=certification)

    if specialization:
        guides = guides.filter(specializations__icontains=specialization)

    if search:
        guides = guides.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(specializations__icontains=search) |
            Q(bio__icontains=search)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'experience':
        guides = guides.order_by('-years_of_experience')
    elif sort_by == 'price_low':
        guides = guides.order_by('daily_rate_usd')
    elif sort_by == 'price_high':
        guides = guides.order_by('-daily_rate_usd')
    else:
        guides = guides.order_by('-average_rating', '-years_of_experience')

    # Pagination
    paginator = Paginator(guides, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_certification': certification,
        'current_specialization': specialization,
        'current_sort': sort_by,
        'search_query': search,
    }
    return render(request, 'tours/guide_list.html', context)


def guide_detail(request, pk):
    """Tour guide detail view."""
    guide = get_object_or_404(
        TourGuide.objects.select_related('user').prefetch_related('parks_covered'),
        pk=pk,
        is_available=True
    )

    # Get guide's tours (if any)
    tours = TourPackage.objects.filter(
        availability__assigned_guide=guide,
        is_active=True
    ).distinct()[:6]

    context = {
        'guide': guide,
        'tours': tours,
    }
    return render(request, 'tours/guide_detail.html', context)

@login_required
def tour_compare(request):
    """Compare multiple tours."""
    tour_ids = request.GET.getlist('tours')

    if not tour_ids:
        return render(request, 'tours/tour_compare.html', {'tours': []})

    tours = TourPackage.objects.filter(
        id__in=tour_ids,
        is_active=True
    ).prefetch_related('parks_visited')[:4]  # Limit to 4 tours

    context = {
        'tours': tours,
    }
    return render(request, 'tours/tour_compare.html', context)
