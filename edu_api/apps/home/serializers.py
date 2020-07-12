from rest_framework import serializers, exceptions
from home.models import *

# 轮询图片
class BannerModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定序列化的模型
        model = Banner
        fields = ("img", "link")

# 导航栏
class NavModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nav
        fields = ('title','link')
