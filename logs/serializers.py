from rest_framework import serializers
from .models import *


class LogsSerialiser(serializers.ModelSerializer):
    addtime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Logs
        fields = '__all__'
        depth = 1






