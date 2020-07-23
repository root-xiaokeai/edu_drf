from my_task.main import app
# celery的任务必须写在tasks的文件中，别的文件名称不识别
from utils.exceptions import logger
from utils.send_msg import Message


@app.task(name="send_sms")  # name可以指定当前任务的名称，如果不填写，则使用默认的函数名作为任务名
def send_sms():
    print("这是发送短信的方法")

    return "hello"