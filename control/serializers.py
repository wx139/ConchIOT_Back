from rest_framework import serializers
from device.models import *
from .models import *


class DeviceListSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = ['id','name','sn','num','address','type','group','building','status','switch','lng','lat','remarks']
        depth = 1

class ParamsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = DeviceParams
        fields = "__all__"
        depth = 1


