from django.contrib import admin
from django.urls import path, include

from payments import views

app_name = 'payments'
urlpatterns = [
    path('ali/',views.AliPayAPIView.as_view()),
    path('result/',views.AliPayResultAPIView.as_view())
]