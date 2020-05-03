from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

class RealTimeDataConsumer(WebsocketConsumer):
    def connect(self):
        # 从打开到使用者的WebSocket连接的chat/routing.py中的URL路由中获取'room_name'参数。
        self.deviceid = self.scope['url_route']['kwargs']['deviceid']
        print('WebSocket建立连接：', self.deviceid)
        # 直接从用户指定的房间名称构造通道组名称
        self.room_group_name = 'msg_%s' % self.deviceid

        # 加入房间
        async_to_sync(self.channel_layer.group_add)(
            self.deviceid,
            self.channel_name
        )  # async_to_sync(…)包装器是必需的，因为ChatConsumer是同步WebsocketConsumer，但它调用的是异步通道层方法。(所有通道层方法都是异步的。)

        # 接受WebSocket连接。
        self.accept()
        simple_username = 'wangxiang'  # 获取session中的值

        async_to_sync(self.channel_layer.group_send)(
            self.deviceid,
            {
                'type': 'chat_message',
                'message': '@{} 已加入房间'.format(simple_username)
            }
        )


    def disconnect(self, close_code):
        print('WebSocket关闭连接')
        # 离开房间
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    # 从WebSocket中接收消息
    def receive(self, text_data=None, bytes_data=None):
        print('WebSocket接收消息：', text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 发送消息到房间
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )


    # 从房间中接收消息
    def chat_message(self, event):
        message = event['message']

        # 发送消息到WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

