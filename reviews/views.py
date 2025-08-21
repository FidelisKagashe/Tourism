from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Avg, Count
from .models import Review, ReviewHelpful
from .forms import ReviewForm
from tours.models import TourPackage
from parks.models import NationalPark
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from django.db import transaction, IntegrityError

class ReviewListView(ListView):
    """
    ListView for reviews with search & filters.
    Supported GET params: type, rating, search, page
    """
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 12

    def get_queryset(self):
        """
        Build queryset without relying on a custom manager method.
        """
        qs = (
            Review.objects
            .filter(is_approved=True)  # <-- explicit filter so no custom manager required
            .select_related('user', 'tour_package', 'national_park')
            .prefetch_related('images')
        )

        review_type = (self.request.GET.get('type') or '').strip()
        rating = (self.request.GET.get('rating') or '').strip()
        search = (self.request.GET.get('search') or '').strip()

        # Validate review_type against choices
        valid_types = {choice[0] for choice in Review.REVIEW_TYPES}
        if review_type in valid_types:
            qs = qs.filter(review_type=review_type)

        # rating filter
        if rating:
            try:
                r = int(rating)
            except ValueError:
                r = None
            if r and 1 <= r <= 5:
                qs = qs.filter(rating=r)

        # multi-field search
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(tour_package__title__icontains=search) |
                Q(national_park__name__icontains=search)
            ).distinct()

        # annotate helpful_count for display (uses ReviewHelpful related_name)
        qs = qs.annotate(helpful_count=Count('helpful_votes_detail'))

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_type'] = self.request.GET.get('type', '')
        context['current_rating'] = self.request.GET.get('rating', '')
        context['search_query'] = self.request.GET.get('search', '')

        # keep existing query params (except page) to reuse in pagination links if needed
        query = self.request.GET.copy()
        if 'page' in query:
            query.pop('page')
        context['querystring'] = query.urlencode()
        return context


@method_decorator(login_required, name='dispatch')
class MarkHelpfulView(View):
    """
    Toggle helpful vote for authenticated users.
    POST /reviews/<pk>/helpful/
    Response JSON: { success: True, helpful_count: <int>, action: 'added'|'removed' }
    """
    def post(self, request, pk, *args, **kwargs):
        review = get_object_or_404(Review, pk=pk, is_approved=True)

        # optional: prevent voting on your own review
        if review.user_id == request.user.id:
            return JsonResponse({'success': False, 'error': 'cannot_vote_own_review'}, status=403)

        try:
            with transaction.atomic():
                obj, created = ReviewHelpful.objects.get_or_create(review=review, user=request.user)
                if created:
                    action = 'added'
                else:
                    # toggle: remove existing vote
                    obj.delete()
                    action = 'removed'

                # recompute fresh count and update denormalized field
                fresh_count = ReviewHelpful.objects.filter(review=review).count()
                Review.objects.filter(pk=review.pk).update(helpful_votes=fresh_count)
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'db_error'}, status=500)

        return JsonResponse({'success': True, 'helpful_count': fresh_count, 'action': action})

class ReviewDetailView(DetailView):
    """Review detail view."""
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        return Review.objects.filter(is_approved=True).select_related(
            'user', 'tour_package', 'national_park'
        ).prefetch_related('images')

@login_required
def create_tour_review(request, tour_slug):
    """Create a review for a tour package."""
    tour_package = get_object_or_404(TourPackage, slug=tour_slug, is_active=True)
    
    # Check if user already reviewed this tour
    existing_review = Review.objects.filter(
        user=request.user,
        tour_package=tour_package
    ).first()
    
    if existing_review:
        messages.warning(request, 'You have already reviewed this tour package.')
        return redirect('tours:package_detail', slug=tour_slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.tour_package = tour_package
            review.review_type = 'tour'
            review.save()
            
            # Update tour package rating
            update_tour_package_rating(tour_package)
            
            messages.success(request, 'Thank you for your review!')
            return redirect('tours:package_detail', slug=tour_slug)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'tour_package': tour_package,
    }
    return render(request, 'reviews/create_tour_review.html', context)

@login_required
def create_park_review(request, park_slug):
    """Create a review for a national park."""
    park = get_object_or_404(NationalPark, slug=park_slug, is_active=True)
    
    # Check if user already reviewed this park
    existing_review = Review.objects.filter(
        user=request.user,
        national_park=park
    ).first()
    
    if existing_review:
        messages.warning(request, 'You have already reviewed this national park.')
        return redirect('parks:park_detail', slug=park_slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.national_park = park
            review.review_type = 'park'
            review.save()
            
            messages.success(request, 'Thank you for your review!')
            return redirect('parks:park_detail', slug=park_slug)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'park': park,
    }
    return render(request, 'reviews/create_park_review.html', context)

@login_required
def mark_review_helpful(request, review_id):
    """Mark a review as helpful."""
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id, is_approved=True)
        
        # Check if user already voted
        helpful_vote, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': True}
        )
        
        if not created:
            # Toggle vote
            helpful_vote.is_helpful = not helpful_vote.is_helpful
            helpful_vote.save()
        
        # Update helpful votes count
        helpful_count = ReviewHelpful.objects.filter(
            review=review,
            is_helpful=True
        ).count()
        
        review.helpful_votes = helpful_count
        review.save()
        
        return JsonResponse({
            'success': True,
            'helpful_votes': helpful_count,
            'user_voted': helpful_vote.is_helpful
        })
    
    return JsonResponse({'success': False})

def update_tour_package_rating(tour_package):
    """Update tour package average rating."""
    reviews = Review.objects.filter(
        tour_package=tour_package,
        is_approved=True
    )
    
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        total_reviews = reviews.count()
        
        tour_package.average_rating = round(avg_rating, 2)
        tour_package.total_reviews = total_reviews
        tour_package.save()

class UserReviewListView(LoginRequiredMixin, ListView):
    """List user's reviews."""
    model = Review
    template_name = 'reviews/user_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related(
            'tour_package', 'national_park'
        ).order_by('-created_at')