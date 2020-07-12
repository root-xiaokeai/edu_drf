from user.models import *
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


def get_user_by_account(account):
    try:
        user = UserInfo.objects.filter(Q(username=account) | Q(phone=account)).first()
    except UserInfo.DoesNotExist:
        return None
    else:
        return user


class UserAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        根据账号获取用户对象
        :param request:  请求对象
        :param username:    前端用户输入账号  手机  用户名
        :param password:    密码
        :return:  查询出的用户
        """
        # 两者满足其一即可   根据多条件查询用户
        user = get_user_by_account(username)
        if user and user.check_password(password) or user.is_authenticated:
            return user
        else:
            return None