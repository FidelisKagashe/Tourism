from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ReviewListView.as_view(), name='review_list'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('tour/<slug:tour_slug>/create/', views.create_tour_review, name='create_tour_review'),
    path('park/<slug:park_slug>/create/', views.create_park_review, name='create_park_review'),
    path('<int:review_id>/helpful/', views.mark_review_helpful, name='mark_helpful'),
    path('my-reviews/', views.UserReviewListView.as_view(), name='user_reviews'),
]