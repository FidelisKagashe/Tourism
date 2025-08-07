from django.urls import path
from . import views

app_name = 'parks'

urlpatterns = [
    path('', views.park_list, name='park_list'),
    path('<slug:slug>/', views.park_detail, name='park_detail'),
    path('destinations/', views.destination_list, name='destination_list'),
    path('destinations/<slug:slug>/', views.destination_detail, name='destination_detail'),
    path('wildlife/', views.wildlife_list, name='wildlife_list'),
    path('wildlife/<int:pk>/', views.wildlife_detail, name='wildlife_detail'),
]