import re
from rest_framework import serializers
from user.models import *
from django.contrib.auth.hashers import make_password


class UserModelSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1024, read_only=True, help_text="用户token")
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = UserInfo
        fields = ("username", "password", "phone","token","sms_code")
        extra_kwargs = {
            "username": {
                "read_only": True,
            },
            "password": {
                "write_only": True,
            },
            "phone": {
                "write_only": True
            }
        }

    def validate(self,attrs):
        """验证手机号"""
        phone = attrs.get("phone")
        password = attrs.get("password")
        sms_code = attrs.get("sms_code")  # 用户提交的验证码
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式错误")

        # 验证手机号是否被注册
        user = UserInfo.objects.filter(phone=phone).first()
        if user:
            raise serializers.ValidationError("当前手机号已经被注册")

        #  验证手机号短信验证码是否正确
        # phone_code=attrs.session.get('code')
        # print(phone_code)
        if "123456" != sms_code:
            # 为了防止暴力破解 可以再次设置一个手机号只能验证 n次  累加
            raise serializers.ValidationError("验证码不一致")

        else:
            # attrs.session.clear()  # 清除数据库中的session_data的数据
            return attrs

    def create(self, validated_data):
        """用户信息设置"""
        # 获取密码  进行加密
        pwd = validated_data.get("password")
        # 对密码进行加密
        hash_password = make_password(pwd)

        # 处理用户名  设置默认值   随机生成字符串  手机号
        username = validated_data.get("phone")

        # 添加数据
        user = UserInfo.objects.create(
            phone=username,
            username=username,
            password=hash_password,
        )

        # 为注册成功的用户生成token
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)
        print(user)
        return user
