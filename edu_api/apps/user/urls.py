from django.contrib import admin
from django.urls import path, include
from user import views
from rest_framework_jwt.views import obtain_jwt_token
app_name = 'user1'
urlpatterns = [
    path("login/", obtain_jwt_token),
    path("captcha/", views.CaptchaAPIView.as_view()),
    path("register/",views.UserAPIView.as_view()),
    path('user/',views.User_name.as_view()),
    path("sms/<str:mobile>/", views.SendMessageAPIView.as_view()),
]
