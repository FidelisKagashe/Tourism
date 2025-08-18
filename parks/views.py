from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import NationalPark, Destination, Wildlife, ParkFacility

def park_list(request):
    """List all national parks."""
    parks = NationalPark.objects.filter(is_active=True).order_by('name')
    
    # Filtering
    park_type = request.GET.get('type')
    region = request.GET.get('region')
    search = request.GET.get('search')
    
    if park_type:
        parks = parks.filter(park_type=park_type)
    
    if region:
        parks = parks.filter(region__icontains=region)
    
    if search:
        parks = parks.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(parks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique regions for filter
    regions = NationalPark.objects.filter(is_active=True).values_list('region', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'regions': regions,
        'current_type': park_type,
        'current_region': region,
        'search_query': search,
    }
    return render(request, 'parks/park_list.html', context)

def park_detail(request, slug):
    """Park detail view (defensive: handles related manager, str, or list)."""
    park = get_object_or_404(NationalPark, slug=slug, is_active=True)

    def _safe_fetch(rel, filter_kwargs=None, limit=None):
        """
        rel: related manager / queryset / str / list / tuple
        filter_kwargs: dict of kwargs to pass to `.filter()` when available
        limit: integer max number of items to return (None => no slicing)
        Returns: queryset, list of model instances, or list of dicts (for string data)
        """
        filter_kwargs = filter_kwargs or {}

        # 1) If it's a manager/queryset — do DB filtering & slicing
        if hasattr(rel, "filter"):
            try:
                qs = rel.filter(**filter_kwargs)
            except Exception:
                # if filter fails for some reason, fall back to rel itself
                qs = rel
            return qs[:limit] if limit is not None else qs

        # 2) If it's a string (e.g. comma-separated names), turn into dicts
        if isinstance(rel, str):
            items = [s.strip() for s in rel.split(",") if s.strip()]
            items = [{"name": s} for s in items]
            return items[:limit] if limit is not None else items

        # 3) If it's an iterable/list/tuple of objects or strings, filter in Python
        if isinstance(rel, (list, tuple)):
            items = list(rel)

            # apply simple boolean filter (common case: is_active/is_operational)
            if filter_kwargs:
                key, expected = next(iter(filter_kwargs.items()))
                filtered = []
                for it in items:
                    # if item has the attribute, test it
                    if hasattr(it, key):
                        try:
                            if getattr(it, key) == expected:
                                filtered.append(it)
                        except Exception:
                            # attribute exists but cannot be tested — include conservatively
                            filtered.append(it)
                    else:
                        # no attribute — include conservatively
                        filtered.append(it)
                items = filtered

            return items[:limit] if limit is not None else items

        # Unknown shape — return empty list
        return []

    # Use the safe fetch wrapper for all related sets
    destinations = _safe_fetch(park.destinations, {'is_active': True}, limit=6)
    wildlife = _safe_fetch(park.wildlife, {'is_active': True}, limit=8)
    facilities = _safe_fetch(park.facilities, {'is_operational': True})
    tour_packages = _safe_fetch(park.tour_packages, {'is_active': True}, limit=4)
    reviews = _safe_fetch(park.reviews, {'is_approved': True}, limit=5)

    context = {
        'park': park,
        'destinations': destinations,
        'wildlife': wildlife,
        'facilities': facilities,
        'tour_packages': tour_packages,
        'reviews': reviews,
    }
    return render(request, 'parks/park_detail.html', context)

def destination_list(request):
    """List all destinations."""
    destinations = Destination.objects.filter(is_active=True).select_related('park')
    
    # Filtering
    destination_type = request.GET.get('type')
    park_id = request.GET.get('park')
    search = request.GET.get('search')
    
    if destination_type:
        destinations = destinations.filter(destination_type=destination_type)
    
    if park_id:
        destinations = destinations.filter(park_id=park_id)
    
    if search:
        destinations = destinations.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(destinations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get parks for filter
    parks = NationalPark.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'parks': parks,
        'current_type': destination_type,
        'current_park': park_id,
        'search_query': search,
    }
    return render(request, 'parks/destination_list.html', context)

def destination_detail(request, slug):
    """Destination detail view."""
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    
    # Get related destinations
    related_destinations = Destination.objects.filter(
        park=destination.park,
        is_active=True
    ).exclude(id=destination.id)[:4]
    
    context = {
        'destination': destination,
        'related_destinations': related_destinations,
    }
    return render(request, 'parks/destination_detail.html', context)

def wildlife_list(request):
    """List all wildlife."""
    wildlife = Wildlife.objects.filter(is_active=True)
    
    # Filtering
    category = request.GET.get('category')
    conservation_status = request.GET.get('status')
    big_five = request.GET.get('big_five')
    search = request.GET.get('search')
    
    if category:
        wildlife = wildlife.filter(category=category)
    
    if conservation_status:
        wildlife = wildlife.filter(conservation_status=conservation_status)
    
    if big_five == 'true':
        wildlife = wildlife.filter(is_big_five=True)
    
    if search:
        wildlife = wildlife.filter(
            Q(common_name__icontains=search) |
            Q(scientific_name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(wildlife, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_category': category,
        'current_status': conservation_status,
        'big_five_filter': big_five,
        'search_query': search,
    }
    return render(request, 'parks/wildlife_list.html', context)

def wildlife_detail(request, pk):
    """Wildlife detail view."""
    wildlife = get_object_or_404(Wildlife, pk=pk, is_active=True)
    
    # Get parks where this wildlife can be found
    parks = wildlife.parks.filter(is_active=True)
    
    # Get related wildlife
    related_wildlife = Wildlife.objects.filter(
        category=wildlife.category,
        is_active=True
    ).exclude(id=wildlife.id)[:4]
    
    context = {
        'wildlife': wildlife,
        'parks': parks,
        'related_wildlife': related_wildlife,
    }
    return render(request, 'parks/wildlife_detail.html', context)