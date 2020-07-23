from django.contrib import admin
from django.urls import path, include

from cart import views

app_name = 'cart'
urlpatterns = [
    path('option/', views.CartViewSet.as_view(
        {'post': 'add_cart',
         'get': 'list_cart',
         'patch': 'change_select',
         "put": "change_expire",})),
    path('order/',views.OrderViewSet.as_view({
        'get': 'get_select_course',
    })),
    # 删除
    path('opt/<str:id>/', views.CartAPiew.as_view()),
    # 生成订单
    path('orders/',views.OrderAPIVew.as_view())
]