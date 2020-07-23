import logging

from django.db import transaction
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.generics import CreateAPIView
from course.serializer import OrderModelSerializer

log = logging.getLogger('django')
from course.models import *


# Create your views here.

# 购物车
class CartViewSet(ViewSet):
    # 购物车相关处理
    permission_classes = [IsAuthenticated]

    def add_cart(self, request):
        # 获取课程id
        course_id = request.data.get('course_id')
        # 获取用户id
        user_id = request.user.id
        # 是否勾选
        select = True
        # 有效期
        expire = 0

        # 校验前端提交的参数
        try:
            Course.objects.get(is_show=True, id=course_id)
        except Course.DoesNotExist:
            return Response({'message': '参数有误，课程不存在'}, status=400)

        try:
            # 获取redis连接对象
            redis_connection = get_redis_connection('cart')
            # 将数据存到redis中
            pipeline = redis_connection.pipeline()
            # 管道开启
            pipeline.multi()
            # 商品的信息以及对应的有效期
            pipeline.hset('cart_%s' % user_id, course_id, expire)
            # 被勾选的商品
            pipeline.sadd('selected_%s' % user_id, course_id)
            # 执行
            pipeline.execute()
            course_len = redis_connection.hlen('cart_%s' % user_id)
        except:
            log.error('购物车数据存储失败')
            return Response({'message': '参数有误，购物车添加失败'}, status=507)

        return Response({'message': '购物车商品添加成功', 'cart_length': course_len}, status=200)

    # 展示购物车
    def list_cart(self, request):
        user_id = request.user.id
        redis_connection = get_redis_connection('cart')
        cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)
        select_list_bytes = redis_connection.smembers('selected_%s' % user_id)

        # 循环从mysql找到商品信息
        data = []
        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)
            try:
                # 获取所有的课程信息
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except:
                continue

            # 将购物车所需的信息返回
            data.append({
                'selected': True if course_id_byte in select_list_bytes else False,
                'course_img': 'http://127.0.0.1:8000' + course.course_img.url,
                'name': course.name,
                'id': course.id,
                'expire': expire_id,
                'price': course.price,
                # 新增当前课程对应的有效期
                # 购物车列表需要课程有效期
                "expire_list": course.expire_list,
            })
        return Response(data)

    # 切换购物车商品状态
    def change_select(self, request):
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')
        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except:
            return Response({'message': '参数有误当前商品不存在'}, status=400)

        redis_connection = get_redis_connection('cart')
        if selected:
            redis_connection.sadd('selected_%s' % user_id, course_id)
        else:
            redis_connection.srem('selected_%s' % user_id, course_id)
        return Response({'message': '状态切换成功'})

    # 课程有效期
    def change_expire(self, request):
        """改变redis中课程的有效期"""
        user_id = request.user.id
        expire_id = request.data.get("expire_id")
        course_id = request.data.get("course_id")
        print(course_id, expire_id)

        try:
            course = Course.objects.get(is_show=True, is_delete=False, id=course_id)
            # 如果前端传递来的有效期选项  如果不是0  则修改课程对应的有效期
            if expire_id > 0:
                expire_iem = CourseExpire.objects.filter(is_show=True, is_delete=False, id=expire_id)
                if not expire_iem:
                    raise Course.DoesNotExist()
        except Course.DoesNotExist:
            return Response({"message": "课程信息不存在"})

        connection = get_redis_connection("cart")
        connection.hset("cart_%s" % user_id, course_id, expire_id)

        return Response({"message": "切换有效期成功"})


# 删除
class CartAPiew(APIView):
    permission_classes = [IsAuthenticated]

    # 对购物车数据进行删除
    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        course_id = kwargs.get("id")
        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except:
            Response({'message': '不存在'})
        redis_connection = get_redis_connection('cart')
        selected = redis_connection.sismember('selected_%s' % user_id, course_id)
        if course:
            if selected:
                # 从redis中删除
                redis_connection.hdel('cart_%s' % user_id, course_id)
                # 从redis中查找
                user = redis_connection.hgetall('cart_%s' % user_id)
                data = []
                for i in user:
                    cour_id = int(i)
                    course = Course.objects.get(is_show=True, is_delete=False, pk=cour_id)
                    data.append({
                        'course_img': 'http://127.0.0.1:8000' + course.course_img.url,
                        'name': course.name,
                        'id': course.id,
                        'price': course.price}
                    )
            else:
                return Response({'message': '未勾选'})
        else:
            return Response({'message': '删除失败'})
        return Response({'message': '删除成功', 'course': data})


# 展示订单页面
class OrderViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_select_course(self, request):
        """
        获取购物车中已勾选的商品  返回前端所需的数据
        """

        user_id = request.user.id
        redis_connection = get_redis_connection("cart")

        # 获取当前登录用户的购车中所有的商品
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        # 获取勾选状态
        select_list = redis_connection.smembers("selected_%s" % user_id)

        total_price = 0  # 商品总价
        data = []

        for course_id_byte, expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            # 判断商品id是否在已勾选的的列表中
            if course_id_byte in select_list:
                try:
                    # 获取到的所有的课程信息
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    continue
                # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                original_price = course.price
                expire_text = "永久有效"

                try:
                    if expire_id > 0:
                        course_expire = CourseExpire.objects.get(id=expire_id)
                        # 对应有效期的价格
                        original_price = course_expire.price
                        expire_text = course_expire.expire_text
                except CourseExpire.DoesNotExist:
                    pass

                # 根据已勾选的商品的对应有效期的价格去计算勾选商品的最终价格
                real_expire_price = course.real_expire_price(expire_id)
                # 将购物车所需的信息返回
                data.append({
                    "course_img": 'http://127.0.0.1:8000' + course.course_img.url,
                    "name": course.name,
                    "id": course.id,
                    "expire_text": expire_text,
                    # 活动、有效期计算完成后的  真实价格
                    "real_price": "%.2f" % float(real_expire_price),
                    # 原价
                    "price": original_price,
                    "discount_name": course.discount_name,
                })

                # 商品叠加后的总价
                total_price += float(real_expire_price)

        return Response({"course_list": data, "total_price": total_price, "message": '获取成功'})


# 生成订单
class OrderAPIVew(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.filter(is_delete=False, is_show=True)
    serializer_class = OrderModelSerializer
