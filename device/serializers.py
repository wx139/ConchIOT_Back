from rest_framework import serializers
from .models import *


class DeviceListSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = ['id','name','sn','num','address','type','group','building','status','switch','lng','lat','remarks','param4']
        depth = 1

class Device_GroupSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = ['id','name','sn','num','address','type','group','building','status','switch','lng','lat','remarks']

class GroupListSerialiser(serializers.ModelSerializer):
    device = Device_GroupSerialiser(many=True)
    class Meta:
        model = Group
        fields = ['id','name','icon','building','remarks','device']
        depth = 1

class Group_BuildingSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name','icon','remarks',]


class BuidlingListSerialiser(serializers.ModelSerializer):
    group = GroupListSerialiser(many=True)
    class Meta:
        model = Buidling
        fields = ['id','name','icon','remarks','group','province','city','area','address']
        depth = 1

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model=Buidling
        fields='__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields='__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Devices
        fields='__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=DeviceType
        fields='__all__'


