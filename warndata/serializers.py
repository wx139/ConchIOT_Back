from rest_framework import serializers
from .models import *


class WarnTypeSerialiser(serializers.ModelSerializer):
    class Meta:
        model = warnType
        fields = '__all__'
        depth = 1

class WarnDataSerializer(serializers.ModelSerializer):
    addtime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = warndata
        fields = '__all__'
        depth = 1




