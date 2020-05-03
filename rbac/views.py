from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from .permissions import *
# Create your views here.
from rest_framework.authtoken.models import Token
from django.contrib import auth
from rbac.service.init_permission import init_permission
from logs.models import *
import datetime
# 登录
class LoginView(APIView):
    def post(self,request,format='JSON'):
        try:
            username=request.data.get('username')
            password=request.data.get('password')
            user=auth.authenticate(username=username,password=password)
            response = {}
            if user is not None:
                hasLogin=False
                try:
                    token=Token.objects.get(user=user)
                    hasLogin=True
                    # token.delete()
                except Exception as e:
                    pass
                if hasLogin==True:
                    token = Token.objects.get(user=user)
                else:
                    token=Token.objects.create(user=user)
                response={}
                response['data']={"token":token.key}
                response['code'] = 20000
                content = user.username + '进行登陆操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行登陆操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                response['code']=0
                return Response(response)
        except Exception as e:
            return Response({
                'code': 0,
                'msg': '数据获取失败'
            })

# 登出
class LogoutView(APIView):
    def post(self,request,format=None):
        user=request.user
        try:
            response = {}
            if request.user.is_authenticated:  # 验证Token是否正确
                token = Token.objects.get(user=request.user)
                token.delete()
                response['data'] = 'success'
                response['code'] = 20000
                content = user.username + '进行注销操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行注销操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                response['code'] = 0
                return Response(response)
        except Exception as e:
            content = user.username + '进行注销操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '用户登出失败'
            })


# 注册
class RegisterView(APIView):
    def post(self,request,format='JSON'):
        try:
            username=request.data.get('username')
            password=request.data.get('password')
            user=UserInfo.objects.create(username=username,password=password)
            response = {}
            if user is not None:
                token=Token.objects.get(user=user)
                token.delete()
                token=Token.objects.create(user=user)
                response={}
                response['token']=token.key
                response['code'] = 20000
                content = user.username + '注册；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                response['code']=0
                return Response(response)
        except Exception as e:
            return Response({
                'code': 0,
                'msg': '数据获取失败'
            })


# 用户信息获取
class UserInfoSet(APIView):
    def get(self,request,format='JSON'):
        if request.user.is_authenticated:  # 验证Token是否正确
            serializer = UserInfoSerializer(request.user)
            response = {}
            response['data'] = serializer.data
            response['code'] = 20000
            return Response(response)
        else:
            print("验证失败")
            return Response({"msg": "验证失败"})


class GetInfo(APIView):
    def get(self,request,format='JSON'):
        if request.user.is_authenticated:  # 验证Token是否正确
            # print(request.user.keys)
            return Response({"msg": "验证通过"})
        else:
            print("验证失败")
            return Response({"msg": "验证失败"})


# 获取用户权限列表
class PermissionView(APIView):
    def get(self, request, format='JSON'):
        if request.user.is_authenticated:  # 验证Token是否正确
            # print(request.user.keys)
            backdata=init_permission(request,request.user)
            backjson={}
            backjson['data']=backdata
            backjson['code']=20000
            return Response(backjson)
        else:
            print("验证失败")
            return Response({"msg": "验证失败"})
