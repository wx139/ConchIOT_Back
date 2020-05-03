import os, sys
# 引入mqtt包
import paho.mqtt.client as mqtt
# 使用独立线程运行
from threading import Thread
from .tasks import *
import re
import time
import json
from celery.result import AsyncResult
from datetime import timedelta
from django.db.models.functions import TruncMinute,TruncDay
# 建立mqtt连接
def on_connect(client, userdata, flag, rc):
    print("已经连接上控驰服务器" + str(rc))


# 接收、处理mqtt消息
def on_message(client, userdata, msg):
    # out = str(msg.payload.decode('utf-8'))
    data = bytearray.hex(bytearray(msg.payload))
    # print(msg.topic)
    matchtopic_state=re.match('.*state$',msg.topic)
    matchtopic_stateraw = re.match('.*stateraw$', msg.topic)
    # print(matchtopic_state)
    if matchtopic_stateraw:
        data = bytearray.hex(bytearray(msg.payload))
        sn=msg.topic.split('stateraw')[0]
        # print(sn)
        data_in_mysql_modbus.delay(sn,data)
    if matchtopic_state:
        data = json.loads(str(msg.payload.decode('utf-8')))
        sn = msg.topic.split('state')[0]
        data_in_mysql_json.delay(sn,data)
        # res = AsyncResult(result)  # 参数为task id
        # print(res.result)
    # print(data)
    # out = json.loads(out)

    # 收到消息后执行任务
    # if msg.topic == 'test/newdata':
    #     print(out)



# mqtt客户端启动函数
def mqttfunction():
    global client
    # 使用loop_start 可以避免阻塞Django进程，使用loop_forever()可能会阻塞系统进程
    client.loop_start()
    # client.loop_forever() 有掉线重连功能
    # client.loop_forever(retry_first_connection=True)


client = mqtt.Client(clean_session=True)

# 启动函数
def mqtt_run1():
    client.on_connect = on_connect
    client.on_message = on_message
    # 绑定 MQTT 服务器地址
    broker = '47.97.105.3'
    # broker = '47.93.220.133'
    # MQTT服务器的端口号
    client.connect(broker, 1883, 60)
    client.subscribe("#")
    # client.reconnect_delay_set(min_delay=1, max_delay=2000)
    # 启动
    mqttthread = Thread(target=mqttfunction)
    mqttthread.start()
    # pass



import requests
def test():
    url='http://api.map.baidu.com/geocoder/v2/?address=天津市天津城区和平区&output=json&ak=gGwQlSIqtQy4wDrCiUH4Tcjj07YgjgjS'
    # url = 'http://api.map.baidu.com/geocoder/v2/?address=' + address + '&output=json&ak=gGwQlSIqtQy4wDrCiUH4Tcjj07YgjgjS'
    r = json.loads(requests.get(url).text).result
    print(r)



