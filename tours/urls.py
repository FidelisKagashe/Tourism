from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list, name='tour_list'),
    path('<slug:slug>/', views.tour_detail, name='tour_detail'),
    path('guides/', views.guide_list, name='guide_list'),
    path('guides/<int:pk>/', views.guide_detail, name='guide_detail'),
    path('compare/', views.tour_compare, name='tour_compare'),
]