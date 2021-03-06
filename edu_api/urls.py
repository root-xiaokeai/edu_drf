"""edu_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from django.views.static import serve
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),
    path('user/',include('home.urls')),
    path('user1/',include('user.urls')),
    path('course/',include('course.urls')),
    # 富文本编辑器的路由
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path('cart/',include('cart.urls')),
    path('payments/',include('payments.urls'))
]
# from django.views.static import serve
# from django.conf import settings
# from django.conf.urls import url
# import xadmin
# from xadmin.plugins import xversion
# from django.urls import path,include
# xversion.register_models()
# from home import views
# urlpatterns = [
#     # 指定图片上传的目录 根目录的urls.py
#     url(r'^media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),
#     path('xadmin/', xadmin.site.urls),
#     path('user/',include('home.urls'))
# ]
