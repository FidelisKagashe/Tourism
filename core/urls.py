from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('faq/', views.faq, name='faq'),
    path('historical-sites/', views.historical_sites_list, name='historical_sites_list'),
    path('historical-sites/<slug:slug>/', views.historical_site_detail, name='historical_site_detail'),
]