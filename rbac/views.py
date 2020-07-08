from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from .permissions import *
# Create your views here.
from rest_framework.authtoken.models import Token
from django.contrib import auth
from rest_framework.pagination import PageNumberPagination
from rbac.service.init_permission import init_permission
from logs.models import *
from django.contrib.auth.hashers import make_password
import datetime
import json
# 登录

def getDept(id,depts,dept_arr):
    for dept in depts:
        if dept.parent and dept.parent.id==id:
            dept_arr.append(dept.id)
            dept_arr=(getDept(dept.id,depts,dept_arr))
    return dept_arr

def getLogo(dept):
    if dept.logo==None:
        if dept.parent!=None:
            return getLogo(dept.parent)
        else:
            return None
    else:
        return dept.logo.url

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
            dept=request.user.dept
            logo=getLogo(dept)
            response = {}
            response['data'] = serializer.data
            response['logo']=logo
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



class userList(APIView):
    # 获取用户下设备列表
    def get(self,request,format="JSON"):
        user=request.user
        try:
            query_params=list(request.query_params.keys())
            kwargs={

            }
            dept_id=user.dept.id
            dept_arr=[]
            depts=Department.objects.all()
            getDept(dept_id,depts,dept_arr).append(dept_id)
            if 'username' in query_params :
                kwargs['username__contains'] = request.query_params['username']
            kwargs['dept_id__in']=dept_arr
            user_list=UserInfo.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 2  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(user_list, request, self) # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = UserListSerialiser(page_list, many=True)
            jsondata={
            }
            jsondata['code']=20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items']=ret.data
            content=user.username+'进行获取用户列表操作；结果：成功！'
            Logs.objects.create(content=content,user=user,addtime=datetime.datetime.now(),ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行用户设备列表操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])

            return Response({
                'code': 0,
                'msg': '设备列表获取失败'
            })

    # 删除多个设备信息
    def delete(self,request):
        user=request.user
        try:
            ids=request.data['userids']
            devices=UserInfo.objects.filter(id__in=ids)
            devices.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['delete_ids']=ids
            content = user.username + '进行批量删除用户操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])

            return Response(jsondata)
        except:
            content = user.username + '进行批量删除用户操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })

#编辑查询单个用户
class userSingle(APIView):
    # 新增用户
    def post(self, request):
        user=request.user
        try:
            json_data = request.data.copy()
            deviceExit = UserInfo.objects.filter(username=json_data['username'])
            if deviceExit:
                return Response({
                    'code': 20000,
                    'tag': 1,
                    'msg': '数据重复'
                })
            ser=None
            json_data['roles'] = [json_data['roles'],]
            if json_data['datatag']==1:
                json_data['password']=make_password('abcd!234')
            else:
                json_data['password']=make_password(json_data['password'])
            ser = UserSerializer(data=json_data)
            if ser.is_valid():
                ser.save()
                response={}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行新增用户操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行新增设备操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                print(ser.errors)
                return Response(json.dumps(ser.errors))
        except:
            content = user.username + '进行新增设备操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个设备信息
    def delete(self,request):
        user=request.user
        try:
            id=request.data['userid']
            users=UserInfo.objects.filter(id=id)
            users.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['id']=id
            content = user.username + '进行删除单个用户操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行删除单个用户操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '用户删除失败'
            })

    # 修改单个设备信息
    def put(self,request):
        user=request.user
        try:
            id = request.data['userid']
            userinfo = UserInfo.objects.get(id=id)
            json_data = request.data.copy()
            json_data['roles'] = [json_data['roles'],]
            # json_data.pop('password')
            # json_data.pop('roles')

            ser = UserUpdataSerializer(instance=userinfo, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行修改用户操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行修改用户操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '进行修改用户操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })



# 获取角色列表
class roleList(APIView):
    # 获取类型列表
    def get(self, request, format="JSON"):
        user = request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'title' in query_params:
                kwargs['title__contains'] = request.query_params['title']
            kwargs['dept_id__in']=dept_arr
            print(dept_arr)
            type_list = Role.objects.filter(**kwargs)
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 20  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(type_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = Roleserializer(page_list, many=True)
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items'] = ret.data
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备列表获取失败'
            })


#编辑查询单个角色
class roleSingle(APIView):


    # 新增角色
    def post(self, request):
        user=request.user
        try:
            json_data = request.data.copy()
            # deviceExit = Role.objects.filter(title=json_data['title'])
            # if deviceExit:
            #     return Response({
            #         'code': 20000,
            #         'tag': 1,
            #         'msg': '数据重复'
            #     })
            ser=None
            ser = Roleaddserializer(data=json_data)
            if ser.is_valid():
                ser.save()
                response={}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行新增角色操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行新增角色操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                print(ser.errors)
                return Response(json.dumps(ser.errors))
        except:
            content = user.username + '进行新增角色操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个角色
    def delete(self,request):
        user=request.user
        try:
            id=request.data['roleid']
            role=Role.objects.filter(id=id)
            role.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['id']=id
            content = user.username + '进行删除单个角色操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行删除单个角色操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })

    # 修改单个角色
    def put(self,request):
        user=request.user
        try:
            id = request.data['roleid']
            json_data = request.data.copy()
            role = Role.objects.get(id=id)
            ser = Roleaddserializer(instance=role, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行修改角色操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行修改角色操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '进行修改角色操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })


# 获取权限列表
class powerList(APIView):
    # 获取类型列表
    def get(self, request, format="JSON"):
        try:
            per_list = Permission.objects.filter()
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 100  # 设置每页的条数
            # page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            # page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            page.max_page_size =50  # 每页的最大数据条数

            page_list = page.paginate_queryset(per_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = PowerSerializer(page_list, many=True)
            for data in ret.data:
                data['children']=[]

            for data in ret.data:
                if data['parent']:
                    for vdata in ret.data:
                        if vdata['id']==data['parent']:
                            vdata['children'].append((data))
            Per=[]
            for data in ret.data:
                if data['parent']==None:
                    Per.append(data)
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items'] = Per
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备列表获取失败'
            })


#编辑查询单个角色
class powerSingle(APIView):


    # 修改角色权限
    def put(self,request):
        user=request.user
        try:
            id = request.data['id']
            json_data = request.data.copy()
            role = Role.objects.get(id=id)
            ser = Powerserializer(instance=role, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行角色权限分配操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行角色权限分配操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '进行角色权限分配操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })


# 获取组织列表
class orgList(APIView):
    # 获取类型列表
    def get(self, request, format="JSON"):
        user=request.user
        try:
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'name' in query_params:
                kwargs['name__contains'] = request.query_params['name']
            dep_list = Department.objects.filter(**kwargs)
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 200  # 设置每页的条数

            page.max_page_size = 50  # 每页的最大数据条数

            page_list = page.paginate_queryset(dep_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = OrgSerializer(page_list, many=True)
            for data in ret.data:
                data['children']=[]

            for data in ret.data:
                if data['parent']:
                    for vdata in ret.data:
                        if vdata['id']==data['parent']['id']:
                            vdata['children'].append((data))
            Per=[]
            for data in ret.data:
                for vdata in ret.data:
                    if 'children' in vdata and len(vdata['children'])==0:
                        vdata.pop('children')
                if data['id']==user.dept.id:
                    Per.append(data)

            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items'] = Per
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备列表获取失败'
            })


#编辑查询单个组织
class orgSingle(APIView):


    # 新增组织
    def post(self, request):
        user=request.user
        try:
            json_data = request.data.copy()
            # deviceExit = Department.objects.filter(title=json_data['title'])
            # if deviceExit:
            #     return Response({
            #         'code': 20000,
            #         'tag': 1,
            #         'msg': '数据重复'
            #     })
            ser=None
            # json_data['parent']=Department.objects.get(id=json_data['parent'])
            ser = DerpartmentSerializer(data=json_data)

            if ser.is_valid():
                ser.save()
                response={}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行新增组织操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行新增组织操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                print(ser.errors)
                return Response(json.dumps(ser.errors))
        except:
            content = user.username + '进行新增组织操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个角色
    def delete(self,request):
        user=request.user
        try:
            id=request.data['orgid']
            dept_arr = []
            depts = Department.objects.all()
            dept_arr=getDept(id, depts, dept_arr)
            if(len(dept_arr)>0):
                return Response({
                            'code': 20000,
                            'tag': 1,
                            'msg': '该组织存在子组织,不可删除'
                        })
            users=UserInfo.objects.filter(dept_id=id)
            if (len(users) > 0):
                return Response({
                    'code': 20000,
                    'tag': 2,
                    'msg': '该组织存在人员,不可删除'
                })
            role=Department.objects.filter(id=id)
            role.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['id']=id
            content = user.username + '进行删除单个组织操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行删除单个角色操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })

    # 修改单个组织
    def put(self,request):
        user=request.user
        try:
            id = request.data['orgid']
            json_data = request.data.copy()
            org = Department.objects.get(id=id)
            print(org)
            print(json_data)
            ser = OrgSerializer(instance=org, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行修改组织操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行修改组织操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '进行修改组织操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })
