from my_task.main import app


@app.task(name="check_order")
def check_order():
    """完成过期取消订单"""
    print("根据时间点判断订单支付时间是否超时")