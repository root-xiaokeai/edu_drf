from django.shortcuts import render
from rest_framework.generics import ListAPIView
from edu_api.settings.constans import *
from home.models import Banner, Nav
from home.serializers import BannerModelSerializer, NavModelSerializer

# 轮询图片
class BannerListAPIView(ListAPIView):
    queryset = Banner.objects.filter(is_show=True, is_delete=False).order_by("-orders")[:banner]
    serializer_class = BannerModelSerializer

# 导航栏
# Create your views here.
class NavListAPIView(ListAPIView):
    queryset = Nav.objects.filter(is_show=True, is_delete=False).order_by("orders")[:nav]
    serializer_class = NavModelSerializer
