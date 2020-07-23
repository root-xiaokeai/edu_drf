import requests


class Message(object):

    def __init__(self, api_key):
        # 账号唯一标识
        self.api_key = api_key
        # 单条短信发送接口
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_message(self, phone, code):
        """
        短信发送的实现
        :param phone: 前端传递的手机号
        :param code: 随机验证码
        :return:
        """
        params = {
            "apikey": self.api_key,
            'mobile': phone,
            'text': "【焦海鹏text】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        # 可以发送http请求
        req = requests.post(self.single_send_url, data=params)
        print(req)


if __name__ == '__main__':
    # message = Message("40d6180426417bfc57d0744a362dc108")
    message = Message("bb29698fb5e23821479d6fa1e3c33480")
    message.send_message("18832310320", "20010413")
