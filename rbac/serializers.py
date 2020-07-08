from .models import *
from rest_framework import serializers

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Role
        fields=('id','title','permissions')
        depth = 1

class Roleserializer(serializers.ModelSerializer):
    class Meta:
        model=Role
        fields=('id','title','permissions','remarks','dept')
        depth = 1

class Roleaddserializer(serializers.ModelSerializer):
    class Meta:
        model=Role
        fields=('title','permissions','remarks','dept')

class Powerserializer(serializers.ModelSerializer):
    class Meta:
        model=Role
        fields=('id','permissions')


class UserInfoSerializer(serializers.ModelSerializer):
    roles=RolesSerializer(many=True)
    class Meta:
        model=UserInfo
        fields=('id','username','email','roles','mobile','dept')

class UserSerializer(serializers.ModelSerializer):
    # roles=RolesSerializer(read_only=True,many=True)
    class Meta:
        model=UserInfo
        fields=('username','email','roles','mobile','password','dept')

class UserUpdataSerializer(serializers.ModelSerializer):
    # roles=RolesSerializer(read_only=True,many=True)
    class Meta:
        model=UserInfo
        fields=('username','email','roles','mobile','dept')



# class MenuSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Menu
#         fields='__all__'
class PerSerializer(serializers.ModelSerializer):
    # children=device
    class Meta:
        model = Permission
        fields = ['id','title','parent']

class PowerSerializer(serializers.ModelSerializer):
    # children=PerSerializer(many=True)
    # children=device
    class Meta:
        model = Permission
        fields = ['id','title','parent',]

class OrgSerializer(serializers.ModelSerializer):
    # roles=RolesSerializer(many=True)
    class Meta:
        model=Department
        fields=('id','name','parent','description')
        depth=1

class DerpartmentSerializer(serializers.ModelSerializer):
    # roles=RolesSerializer(many=True)
    class Meta:
        model=Department
        fields=('id','name','parent','description')

class UserListSerialiser(serializers.ModelSerializer):
    roles = RolesSerializer(read_only=True, many=True)
    # dept=OrgSerializer(read_only=True, many=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = UserInfo
        fields = ('id','username', 'email', 'roles', 'avatar','mobile','last_login','dept')
        depth=1