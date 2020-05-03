from rest_framework import serializers
from device.models import *

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






