from my_task.main import app
from celery.schedules import crontab
# 任务队列的连接的地址
broker_url = "redis://127.0.0.1:6379/11"
# 结果队列的连接地址
result_backend = "redis://127.0.0.1:6379/12"

# 定时任务调度
app.conf.beat_schedule = {
    'check_order_our_time': {
        # 本次调度的任务
        'task': 'check_order',  # 注意，任务必须已经注册到了main中
        # 定时任务的调度周期
        # 'schedule': 30.0,
        'schedule': crontab(),  # 每分钟调度一次
        # 'args': (16, 16)  # 是一个函数，有参数可以传递  没参数无需传递
    },
}