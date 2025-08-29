from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from parks.models import NationalPark, Destination
from tours.models import TourPackage
from reviews.models import Review
from .models import ContactMessage, Newsletter, HistoricalSite
from .forms import ContactForm, NewsletterForm

def home(request):
    """Homepage view."""
    # Featured content
    featured_parks = NationalPark.objects.filter(
        is_active=True, featured=True
    ).order_by('?')[:6]
    
    featured_tours = TourPackage.objects.filter(
        is_active=True, is_featured=True
    ).select_related().order_by('?')[:6]
    
    # NEW: featured destinations for the homepage marquee
    featured_destinations = Destination.objects.filter(
        is_active=True
    ).select_related('park').order_by('?')[:12]

    # Recent reviews
    recent_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('user', 'tour_package', 'national_park').order_by('-created_at')[:6]
    
    # Statistics
    stats = {
        'total_parks': NationalPark.objects.filter(is_active=True).count(),
        'total_tours': TourPackage.objects.filter(is_active=True).count(),
        'total_reviews': Review.objects.filter(is_approved=True).count(),
        'average_rating': Review.objects.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0,
    }
    
    context = {
        'featured_parks': featured_parks,
        'featured_tours': featured_tours,
        'featured_destinations': featured_destinations,
        'recent_reviews': recent_reviews,
        'stats': stats,
    }
    return render(request, 'core/home.html', context)

def about(request):
    """About page view."""
    return render(request, 'core/about.html')

def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

def search(request):
    """Global search view."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'core/search.html', {
            'query': query,
            'parks': [],
            'tours': [],
            'total_results': 0,
        })
    
    # Search parks
    parks = NationalPark.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query) |
        Q(region__icontains=query),
        is_active=True
    ).distinct()
    
    # Search tours
    tours = TourPackage.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(short_description__icontains=query),
        is_active=True
    ).distinct()
    
    # Pagination
    parks_paginator = Paginator(parks, 6)
    tours_paginator = Paginator(tours, 6)
    
    parks_page = request.GET.get('parks_page', 1)
    tours_page = request.GET.get('tours_page', 1)
    
    parks_results = parks_paginator.get_page(parks_page)
    tours_results = tours_paginator.get_page(tours_page)
    
    total_results = parks.count() + tours.count()
    
    context = {
        'query': query,
        'parks': parks_results,
        'tours': tours_results,
        'total_results': total_results,
    }
    return render(request, 'core/search.html', context)

def newsletter_signup(request):
    """Newsletter signup AJAX endpoint."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing to our newsletter!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'You are already subscribed to our newsletter.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'core/privacy_policy.html')

def terms_of_service(request):
    """Terms of service page."""
    return render(request, 'core/terms_of_service.html')

def faq(request):
    """FAQ page."""
    return render(request, 'core/faq.html')

def historical_sites_list(request):
    """
    List historical sites with filters: type, region, search, page.
    """
    # sanitize GET params (keep as strings for template comparisons)
    site_type = (request.GET.get('type') or '').strip()
    region = (request.GET.get('region') or '').strip()
    search = (request.GET.get('search') or '').strip()
    page_number = request.GET.get('page')

    # Base queryset
    sites = HistoricalSite.objects.filter(is_active=True).order_by('name')

    # Apply filters
    if site_type:
        sites = sites.filter(site_type=site_type)

    if region:
        # match region exactly (case-insensitive)
        sites = sites.filter(region__iexact=region)

    if search:
        sites = sites.filter(
            Q(name__icontains=search) |
            Q(short_description__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        ).distinct()

    # Pagination
    paginator = Paginator(sites, 12)
    page_obj = paginator.get_page(page_number)

    # Unique regions for filter (exclude blank/null, ordered)
    regions = (
        HistoricalSite.objects
        .filter(is_active=True)
        .exclude(region__isnull=True)
        .exclude(region__exact='')
        .values_list('region', flat=True)
        .distinct()
        .order_by('region')
    )

    # Site types from model choices so template values always match DB
    site_types = HistoricalSite.SITE_TYPES

    context = {
        'page_obj': page_obj,
        'regions': regions,
        'site_types': site_types,
        'current_type': site_type,
        'current_region': region,
        'search_query': search,
    }
    return render(request, 'core/historical_sites_list.html', context)

def historical_site_detail(request, slug):
    """Historical site detail view."""
    site = get_object_or_404(HistoricalSite, slug=slug, is_active=True)
    
    # Get related sites
    related_sites = HistoricalSite.objects.filter(
        region=site.region,
        is_active=True
    ).exclude(id=site.id)[:4]
    
    context = {
        'site': site,
        'related_sites': related_sites,
    }
    return render(request, 'core/historical_site_detail.html', context)

def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'core/privacy_policy.html')

def terms_of_service(request):
    """Terms of service page."""
    return render(request, 'core/terms_of_service.html')