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

class ReviewListView(ListView):
    """List all reviews."""
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True).select_related(
            'user', 'tour_package', 'national_park'
        ).prefetch_related('images')
        
        # Filter by type
        review_type = self.request.GET.get('type')
        if review_type in ['tour', 'park']:
            queryset = queryset.filter(review_type=review_type)
        
        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    queryset = queryset.filter(rating=rating)
            except ValueError:
                pass
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_type'] = self.request.GET.get('type', '')
        context['current_rating'] = self.request.GET.get('rating', '')
        return context

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