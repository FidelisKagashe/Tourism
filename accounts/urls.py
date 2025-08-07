from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('profile/extended/', views.ExtendedProfileUpdateView.as_view(), name='extended_profile_update'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('reviews/', views.user_reviews, name='user_reviews'),
    path('documents/', views.user_documents, name='user_documents'),
]