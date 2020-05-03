from .models import *
from rest_framework import serializers

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Role
        fields=('id','title')

class UserInfoSerializer(serializers.ModelSerializer):
    roles=RolesSerializer(read_only=True,many=True)
    class Meta:
        model=UserInfo
        fields=('username','email','roles','avatar')

# class MenuSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Menu
#         fields='__all__'