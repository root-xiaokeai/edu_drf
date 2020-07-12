from django.shortcuts import render
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status
from edu_api.libs.geetest import GeetestLib
from rest_framework.generics import CreateAPIView
from user.utils import get_user_by_account
from user.models import *
from user.serializers import UserModelSerializer
import random
from utils.send_msg import Message

pc_geetest_id = "6f91b3d2afe94ed29da03c14988fb4ef"
pc_geetest_key = "7a01b1933685931ef5eaf5dabefd3df2"

"""极验验证码"""


class CaptchaAPIView(APIView):
    """极验验证码"""

    user_id = 0
    status = False

    def get(self, request, *args, **kwargs):
        """获取验证码"""

        username = request.query_params.get('username')
        user = get_user_by_account(username)
        if user is None:
            return Response({"message": "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request, *args, **kwargs):
        print(111)
        """验证验证码"""
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        print(gt)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        print(challenge, validate, seccode)
        # 判断用户是否存在
        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


# 注册
class UserAPIView(CreateAPIView):
    """用户注册"""
    queryset = UserInfo.objects.all()
    serializer_class = UserModelSerializer


# 手机号是否重复
class User_name(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('phone')
        user = UserInfo.objects.filter(phone=username)
        if user:
            return Response('已有用户')
        else:
            return Response('手机号合法')


# 短信
class SendMessageAPIView(APIView):

    def get(self, request, mobile):
        """
        获取验证码  为手机号生成验证码并发送
        :param request:
        :param mobile: 手机号
        :return:
        """
        # 2. 生成随机的短信验证码
        code = "%06d" % random.randint(0, 999999)

        # 3. 将验证码保存到session中
        # request.session['code'] = code

        # 4. 调用方法  完成短信的发送
        try:
            # message = Message("40d6180426417bfc57d0744a362dc108")
            message=Message("bb29698fb5e23821479d6fa1e3c33480")
            message.send_message(mobile, code)
            # message.send_message('13070185809', '123567')
        except:
            return Response({"message": "短信发送失败", "status": 400})

        # 5. 响应回去
        return Response({"message": "发送短信成功", 'status': 200})
