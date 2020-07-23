from django.db import transaction
from django_redis import get_redis_connection
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from course.models import *


class Course_Lesson(ModelSerializer):
    '''课时查询'''

    class Meta:
        model = CourseLesson
        fields = ['name']


class BookModelSerializer(ModelSerializer):
    '''课程章节'''

    class Meta:
        model = CourseChapter
        fields = ['chapter', 'name', 'summary']


class CourseCategorySerializer(ModelSerializer):
    """课程分类"""

    class Meta:
        model = CourseCategory
        fields = ["id", "name"]


class CourseTeacherSerializer(ModelSerializer):
    """课程所属老师的序列化器"""

    class Meta:
        model = Teacher
        fields = ("id", "name", "title", "brief", 'signature', 'image')


class CourseModelSerializer(ModelSerializer):
    """课程列表"""

    # 序列化器嵌套查询老师信息
    teacher = CourseTeacherSerializer()

    # 章节
    # course_category = BookModelSerializer()
    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students",
                  "lessons", "pub_lessons", "price", "teacher",
                  "lesson_list", 'level_name', 'course_types', 'course',
                  'course_video', 'brief_html', "discount_name", "real_price",
                  "active_time", "brief_html"]


# 订单序列器
class OrderModelSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'pay_type')

        extra_kwargs = {
            'id': {'read_only': True},
            'order_number': {'read_only': True},
            'pay_type': {'write_only': True}
        }

    def validate(self, attrs):
        # 对数据进行验证
        pay_type = attrs.get('pay_type')
        try:
            Order.pay_choices[pay_type]
        except:
            raise serializers.ValidationError('您当前选择的支付方式不允许')
        return attrs

    def create(self, validated_data):
        """生成订单   与  订单详情 """
        redis_connection = get_redis_connection("cart")

        # 通过context获取到request对象
        user_id = self.context['request'].user.id
        # user_id=1
        incr = redis_connection.incr("order")
        # 生成唯一的订单号  时间戳 用户id  随机字符串  0001  7862
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user_id + "%06d" % incr
        # 生成订单
        order = Order.objects.create(order_title="百知教育在线课程订单", total_price=0, real_price=0, order_number=order_number,
                                     order_status=0, pay_type=validated_data.get("pay_type"), credit=0, coupon=0,
                                     order_desc="选择这个课程是你极其优秀的决定", user_id=user_id, )

        # 事务开启
        with transaction.atomic():

            # 记录下事务回滚的点
            rollback_id = transaction.savepoint()
            # 生成订单详情
            # 从购物车获取所有已勾选的商品
            cart_list = redis_connection.hgetall("cart_%s" % user_id)
            select_list = redis_connection.smembers("selected_%s" % user_id)

            for course_id_byte, expire_id_byte in cart_list.items():
                course_id = int(course_id_byte)
                expire_id = int(expire_id_byte)
                # 判断商品id是否在已勾选的的列表中
                if course_id_byte in select_list:

                    try:

                        # 获取到的所有的课程信息
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        """课程不存在则不再进行订单详情的生成 已生成好的订单表也不再保存"""
                        """回滚事务"""
                        transaction.savepoint_rollback(rollback_id)
                        raise serializers.ValidationError("对不起，当前商品不存在")

                    # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                    original_price = course.price

                    try:
                        if expire_id > 0:
                            course_expire = CourseExpire.objects.get(id=expire_id)
                            # 对应有效期的价格
                            original_price = course_expire.price
                    except CourseExpire.DoesNotExist:
                        pass

                    # 根据已勾选的商品的对应有效期的价格去计算勾选商品的最终价格
                    real_expire_price = course.real_expire_price(expire_id)
                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(
                                order=order,
                                course=course,
                                expire=expire_id,
                                price=original_price,
                                real_price=real_expire_price,
                                discount_name=course.discount_name
                            )
                        # 删除以生成订单的课程
                        courses_id = course.id
                        print(courses_id)
                        redis_connection.hdel('cart_%s' % user_id, courses_id)
                    except:
                        """回滚事务"""
                        transaction.savepoint_rollback(rollback_id)
                        raise serializers.ValidationError("订单生成失败")
                    # 计算订单的总价
                    # course_id = course.id
                    order.total_price += float(original_price)
                    order.real_price += float(real_expire_price)
                order.save()
            return order
