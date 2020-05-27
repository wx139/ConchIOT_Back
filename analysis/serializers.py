from rest_framework import serializers
from access.models import *
from device.models import *


class RealTimeListSerialiser(serializers.ModelSerializer):
    addTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = RealTimeData
        fields = ['meaEle','meaVol','tPower','meaHz','tEle','pEle','addTime','params1','params2','params3']
        depth = 1

class ActualDataSerialiser(serializers.ModelSerializer):
    addTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = ActualData
        fields = ['meaEle','meaVol','tPower','meaHz','tEle','pEle','params1','params2','params3','addTime']


class  ActualDataTotalSerialiser(serializers.ModelSerializer):
    addTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = ActualDataTotal
        fields = '__all__'


class ActualDataGroupSerialiser(serializers.ModelSerializer):
    groupname=serializers.CharField(source='group.name')
    addTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = ActualDataGroup
        fields = '__all__'



class ActualDataBuildSerialiser(serializers.ModelSerializer):
    buildname = serializers.CharField(source='build.name')
    addTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = ActualDataBuild
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    device=DeviceSerializer(many=True)
    children=device
    class Meta:
        model = Group
        fields = ['id','name','device','children']

class BuildSerialiser(serializers.ModelSerializer):
    group = GroupSerializer(many=True)
    children=group
    class Meta:
        model = Buidling
        fields = ['id','name','group','children']

