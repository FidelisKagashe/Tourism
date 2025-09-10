from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.db.models import F, Q
from django.contrib.auth.decorators import login_required
from .models import TourPackage, TourGuide, TourAvailability

def tour_list(request):
    """List all tour packages."""
    tours = TourPackage.objects.filter(is_active=True).select_related().prefetch_related('parks_visited')
    
    # Filtering
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    duration = request.GET.get('duration')
    featured = request.GET.get('featured')
    popular = request.GET.get('popular')
    search = request.GET.get('search')
    
    if category:
        tours = tours.filter(category=category)
    
    if difficulty:
        tours = tours.filter(difficulty_level=difficulty)
    
    if duration:
        if duration == 'short':
            tours = tours.filter(duration_days__lte=3)
        elif duration == 'medium':
            tours = tours.filter(duration_days__range=(4, 7))
        elif duration == 'long':
            tours = tours.filter(duration_days__gte=8)
    
    if featured == 'true':
        tours = tours.filter(is_featured=True)
    
    if popular == 'true':
        tours = tours.filter(is_popular=True)
    
    if search:
        tours = tours.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'duration':
        tours = tours.order_by('duration_days')
    elif sort_by == 'rating':
        tours = tours.order_by('-average_rating')
    elif sort_by == 'name':
        tours = tours.order_by('title')
    else:
        tours = tours.order_by('-is_featured', '-is_popular', '-created_at')
    
    # Pagination
    paginator = Paginator(tours, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_category': category,
        'current_difficulty': difficulty,
        'current_duration': duration,
        'featured_filter': featured,
        'popular_filter': popular,
        'current_sort': sort_by,
        'search_query': search,
    }
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, slug):
    tour = get_object_or_404(
        TourPackage.objects.select_related().prefetch_related(
            'parks_visited', 'itinerary_days', 'images', 'reviews__user', 'extras'
        ),
        slug=slug,
        is_active=True
    )

    availability = (
        tour.availability
            .filter(is_available=True)
            .filter(
                Q(max_participants__isnull=True) |  # unlimited -> keep
                Q(booked_participants__lt=F('max_participants'))  # spots left
            )
            .order_by('start_date')[:10]
    )

    reviews = tour.reviews.filter(is_approved=True).select_related('user')[:10]
    related_tours = TourPackage.objects.filter(
        category=tour.category, is_active=True
    ).exclude(id=tour.id)[:4]

    context = {'tour': tour, 'availability': availability,
               'reviews': reviews, 'related_tours': related_tours}
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