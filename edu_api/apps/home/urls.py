from django.contrib import admin
from django.urls import path, include
from home import views

app_name = 'user'
urlpatterns = [
    path('home/', views.BannerListAPIView.as_view()),
    path('home_nav/', views.NavListAPIView.as_view())
]
