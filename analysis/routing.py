from django.urls import path
from analysis import consumers

websocket_urlpatterns = [
    # url(r'^ws/msg/(?P<room_name>[^/]+)/$', consumers.SyncConsumer),
    path('ws/realtime/<deviceid>/', consumers.RealTimeDataConsumer),
]