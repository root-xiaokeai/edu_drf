from django.contrib import admin
from django.urls import path, include

from course import views
app_name = 'course'
urlpatterns = [
    path("category/", views.CourseCategoryListAPIView.as_view()),
    path("list/", views.CourseListAPIView.as_view()),
    path("list_filter/", views.CourseFilterListAPIView.as_view()),
    path('chapter/<str:id>/',views.CourseChapterAPIView.as_view())
]
