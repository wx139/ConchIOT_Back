from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Devices
from django.http import FileResponse
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import requests
from django.db.models import Avg, Max, Min,Sum,Count
from access.models import *
import datetime
from logs.models import *
from rbac.models import *

# Create your views here.
def getDept(id,depts,dept_arr):
    for dept in depts:
        if dept.parent and dept.parent.id==id:
            dept_arr.append(dept.id)
            dept_arr=(getDept(dept.id,depts,dept_arr))
    return dept_arr

class deviceList(APIView):
    # 获取用户下设备列表
    def get(self,request,format="JSON"):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params=list(request.query_params.keys())
            kwargs={

            }
            if 'sn' in query_params :
                kwargs['sn__contains'] = request.query_params['sn']
            if 'group' in query_params and request.query_params['group']!='':
                kwargs['group__id'] = request.query_params['group']
            if 'building' in query_params and request.query_params['building']!='':
                kwargs['building__id'] = request.query_params['building']
            if 'type' in query_params and request.query_params['type']!='':
                kwargs['type__id'] = request.query_params['type']
            if 'name' in query_params:
                kwargs['name__contains'] = request.query_params['name']
            kwargs['user__dept_id__in']=dept_arr
            devices_list=Devices.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 2  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(devices_list, request, self) # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = DeviceListSerialiser(page_list, many=True)
            jsondata={
            }
            jsondata['code']=20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items']=ret.data
            content=user.username+'进行获取设备列表操作；结果：成功！'
            Logs.objects.create(content=content,user=user,addtime=datetime.datetime.now(),ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行获取设备列表操作；结果：失败！'
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
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            ids=request.data['deviceids']
            devices=Devices.objects.filter(id__in=ids,user__dept_id__in=dept_arr)
            devices.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['delete_ids']=ids
            content = user.username + '进行批量删除设备操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])

            return Response(jsondata)
        except:
            content = user.username + '进行批量删除设备操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })

#编辑查询单个设备
class deviceSingle(APIView):
    # 获取单个设备信息
    def get(self,request,format='JSON'):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            print(dept_arr)
            device_id = request.query_params['deviceid']
            print(device_id)
            device=Devices.objects.get(id=device_id,user__dept_id__in=dept_arr)
            print(device)
            serializer = DeviceListSerialiser(device)
            response = {}
            response['data'] = serializer.data
            response['code'] = 20000
            content = user.username + '进行查询单个设备操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(response)
        except:
            content = user.username + '进行查询单个设备操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '设备获取失败'
            })

    # 新增用户下设备列表
    def post(self, request):
        user=request.user
        try:
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            groupid=json_data['group']
            build=Buidling.objects.get(group__id=groupid)
            json_data['lng']=build.lng
            json_data['lat']=build.lat
            ser=None
            if json_data['datatag']==1:
                deviceExit = Devices.objects.filter(sn=json_data['sn'], num=json_data['num'])
                if deviceExit:
                    return Response({
                        'code': 20000,
                        'tag': 1,
                        'msg': '数据重复'
                    })
                ser = DeviceSerializer(data=json_data)
            else:
                json_list=[]
                if type(json_data['length']=='str'):
                    json_data['length']=int(json_data['length'])
                for i in range(json_data['length']):
                    json_obj = json_data.copy()
                    json_obj['num']=hex(i+1).split('0x')[1]
                    json_obj['name'] = json_data['name']+str(i+1)
                    deviceExit=Devices.objects.filter(sn=json_obj['sn'],num=json_obj['num'])
                    if deviceExit:
                        return  Response({
                            'code': 20000,
                            'tag':1,
                            'msg': '数据重复'
                        })
                    json_list.append(json_obj)
                ser = DeviceSerializer(data=json_list,many=True)
            if ser.is_valid():
                ser.save()
                response={}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行新增设备操作；结果：成功！'
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
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            id=request.data['deviceid']
            devices=Devices.objects.filter(id=id,user__dept_id__in=dept_arr)
            devices.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['id']=id
            content = user.username + '进行删除单个设备操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行删除单个设备操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })

    # 修改单个设备信息
    def put(self,request):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            id = request.data['id']
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            groupid = json_data['group']
            build = Buidling.objects.get(group__id=groupid,user__dept_id__in=dept_arr)
            json_data['lng'] = build.lng
            json_data['lat'] = build.lat
            device = Devices.objects.get(id=id)
            ser = DeviceSerializer(instance=device, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行修改设备操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行修改设备操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '进行修改设备操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })


# 获取用户下分组列表
class groupList(APIView):
    # 获取分组列表
    def get(self, request, format="JSON"):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {}
            if 'building' in query_params:
                kwargs['building__id'] = request.query_params['building']
            if 'name' in query_params:
                kwargs['name__contains'] = request.query_params['name']
            kwargs['user__dept_id__in']=dept_arr
            group_list = Group.objects.filter(**kwargs).order_by()
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 20  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(group_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = GroupListSerialiser(page_list, many=True)
            jsondata = {
            }
            for group in ret.data:
                online=0
                offline=0
                open=0
                close=0
                power=ActualData.objects.filter(device__group_id=group['id']).aggregate(power=Sum('tPower'))
                for device in group['device']:
                    if device['status']=='0':
                        offline+=1
                    else:
                        online+=1
                    if device['switch']=='0':
                        close+=1
                    else:
                        open+=1
                group['power']=power
                group['online'] = online
                group['offline']=offline
                group['open']=open
                group['close']=close
                group['device_total']=len(group['device'])
            jsondata['code'] = 20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items'] = ret.data
            content = user.username + '进行查询分组列表操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行查询分组列表操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '分组列表获取失败'
            })



#获取用户下单个分组的信息
class  groupSingle(APIView):
    # 查询单个分组信息
    def get(self,request,format='JSON'):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            group_id = request.query_params['groupid']
            group = Group.objects.get(id=group_id,user__dept_id__in=dept_arr)
            serializer = GroupListSerialiser(group)
            response = {}
            response['data'] = serializer.data
            response['code'] = 20000
            content = user.username + '进行查询单个分组信息操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(response)
        except:
            content = user.username + '进行查询单个分组信息操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '分组获取失败'
            })

    # 新增分组列表
    def post(self, request):
        user=request.user
        try:
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            ser = GroupSerializer(data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行新增分组操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行新增分组操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response({
                    'code': 0,
                    'msg': '数据写入失败'
                })
        except:
            content = user.username + '进行新增分组操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 修改单个分组信息
    def put(self,request):
        user=request.user
        try:
            id = request.data['id']
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            group = Group.objects.get(id=id)
            ser = GroupSerializer(instance=group, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行修改分组操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行修改分组操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])

                return Response(ser.errors)
        except:
            content = user.username + '进行修改分组操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个分组信息
    def delete(self,request):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            if request.data.__len__()==0:
                id = request.query_params['groupid']
            else:
                id = request.data['groupid']
            group = Group.objects.get(id=id,user__dept_id__in=dept_arr)
            device = group.device.all()
            if len(device) > 0:
                jsondata = {}
                jsondata['code'] = 20000
                jsondata['status'] = 201
                content = user.username + '进行删除分组操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(jsondata)
            group.delete()
            jsondata = {}
            jsondata['code'] = 20000
            jsondata['group'] = id
            content = user.username + '进行删除分组操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行删除分组操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })


# 获取用户下楼层列表
class buildingList(APIView):
    # 获取楼层列表
    def get(self, request, format="JSON"):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'name' in query_params:
                kwargs['name__contains'] = request.query_params['name']
            kwargs['user__dept_id__in']=dept_arr
            buidling_list = Buidling.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 20  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(buidling_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = BuidlingListSerialiser(page_list, many=True)
            jsondata = {
            }
            for building in ret.data:
                online=0
                offline=0
                open=0
                close=0
                total=0
                power=ActualData.objects.filter(device__building_id=building['id']).aggregate(power=Sum('tPower'))
                for group in building['group']:
                    for device in group['device']:
                        total +=1
                        if device['status']=='0':
                            offline+=1
                        else:
                            online+=1
                        if device['switch']=='0':
                            close+=1
                        else:
                            open+=1
                building['power']=power
                building['online']=online
                building['offline']=offline
                building['open']=open
                building['close']=close
                building['device_total']=total
            jsondata['code'] = 20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items'] = ret.data
            content = user.username + '进行获取楼层列表操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行获取楼层列表操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '设备列表获取失败'
            })


#获取、修改用户下单个楼层的信息
class buildingSingle(APIView):
    # 查询单个楼层
    def get(self, request, format="JSON"):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'id' in query_params:
                kwargs['id'] = request.query_params['id']
                kwargs['user__dept_id__in']=dept_arr
                buidling = Buidling.objects.get(**kwargs)
                ret=BuildingSerializer(buidling)
                jsondata={}
                jsondata['code'] = 20000
                jsondata['data'] = ret.data
                content = user.username + '进行查询单个楼层信息操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(jsondata)
        except:
            content = user.username + '进行查询单个楼层信息操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据获取失败'
            })

    # 新增楼层列表
    def post(self, request):
        user=request.user
        try:
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            query_params = list(request.data.keys())
            address=''
            if 'province' in query_params :
                address+=json_data['province']
            if 'city' in query_params:
                address+=json_data['city']
            if 'area' in query_params :
                address+=json_data['area']
            if 'address' in query_params and request.data['address'] != ''  and request.data['address'] != None:
                address += json_data['address']
            url = 'http://api.map.baidu.com/geocoder/v2/?address='+address+'&output=json&ak=gGwQlSIqtQy4wDrCiUH4Tcjj07YgjgjS'
            data=json.loads(requests.get(url).text)
            if(data['status']==0):
                location = data['result']['location']
                # json_data['lng']=
                json_data['lng'] = location['lng']
                json_data['lat'] = location['lat']
            ser = BuildingSerializer(data=json_data)
            if ser.is_valid():
                ser.save()
                jsondata = {}
                jsondata['code'] = 20000
                jsondata['data'] = ser.data
                content = user.username + '进行新增楼层操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(jsondata)
            else:
                content = user.username + '进行新增楼层操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(json.dumps(ser.errors))
        except:
            content = user.username + '进行新增楼层操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 修改单个楼层
    def put(self,request):
        user=request.user
        try:
            id = request.data['id']
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            query_params = list(request.data.keys())
            address = ''
            if 'province' in query_params:
                address += json_data['province']
            if 'city' in query_params:
                address += json_data['city']
            if 'area' in query_params:
                address += json_data['area']
            if 'address' in query_params and request.data['address'] != ''  and request.data['address'] != None:
                address += json_data['address']
            url = 'http://api.map.baidu.com/geocoder/v2/?address=' + address + '&output=json&ak=gGwQlSIqtQy4wDrCiUH4Tcjj07YgjgjS'
            data = json.loads(requests.get(url).text)
            if (data['status'] == 0):
                location = data['result']['location']
                # json_data['lng']=
                json_data['lng'] = location['lng']
                json_data['lat'] = location['lat']
            bulding = Buidling.objects.get(id=id)
            ser = BuildingSerializer(instance=bulding, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '进行修改楼层操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '进行修改楼层操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '进行修改楼层操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个楼层
    def delete(self,request):
        user=request.user
        try:
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            if request.data.__len__()==0:
                id = request.query_params['buildingid']
            else:
                id = request.data['buildingid']
            building = Buidling.objects.get(id=id,user__dept_id__in=dept_arr)
            group=building.group.all()
            if len(group)>0:
                jsondata = {}
                jsondata['code'] = 20000
                jsondata['status'] = 201
                content = user.username + '进行删除楼层操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(jsondata)
            building.delete()
            jsondata = {}
            jsondata['code'] = 20000
            jsondata['status'] = 200
            jsondata['buildingid'] = id
            content = user.username + '进行删除楼层操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行删除楼层操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })




# 获取用户下类型列表
class typeList(APIView):
    # 获取类型列表
    def get(self, request, format="JSON"):
        user=request.user
        try:
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'name' in query_params:
                kwargs['name__contains'] = request.query_params['name']
            type_list = DeviceType.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 20  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(type_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = TypeSerializer(page_list, many=True)
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


#获取、修改用户下单个类型的信息
class typeSingle(APIView):
    # 查询单个楼层
    def get(self, request, format="JSON"):
        try:
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'id' in query_params:
                kwargs['id'] = request.query_params['id']
                buidling = Buidling.objects.get(**kwargs)
                ret=BuildingSerializer(buidling)
                jsondata={}
                jsondata['code'] = 20000
                jsondata['data'] = ret.data
                return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '数据获取失败'
            })

    # 新增楼层列表
    def post(self, request):
        try:
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            ser = BuildingSerializer(data=json_data)
            if ser.is_valid():
                ser.save()
                jsondata = {}
                jsondata['code'] = 20000
                jsondata['data'] = ser.data
                return Response(jsondata)
            else:
                print(ser.errors)
                return Response(json.dumps(ser.errors))
        except:
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 修改单个楼层
    def put(self,request):
        try:
            id = request.data['id']
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            bulding = Buidling.objects.get(id=id)
            ser = BuildingSerializer(instance=bulding, data=json_data)
            if ser.is_valid():
                ser.save()
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                return Response(response)
            else:
                print(ser.errors)
                return Response(ser.errors)
        except:
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个楼层
    def delete(self,request):
        try:
            id = request.data['buildingid']
            building = Buidling.objects.filter(id=id)
            building.delete()
            jsondata = {}
            jsondata['code'] = 20000
            jsondata['buildingid'] = id
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })


class downTempleate(APIView):
    def get(self,request):
        user=request.user
        file = open('./static/设备批量导入模版.xlsx', 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="datain.xlsx"'
        content = user.username + '进行下载模版操作；结果：成功！'
        Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                            ip=request.META['REMOTE_ADDR'])
        return response

