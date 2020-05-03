from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from rest_framework.pagination import PageNumberPagination
from .serializers import *
import json
from logs.models import *
import datetime
# Create your views here.
#获取告警类型列表
class WarnTypeList(APIView):
    # 获取用户下设备列表
    def get(self,request,format="JSON"):
        # user=request.user
        try:
            query_params=list(request.query_params.keys())
            kwargs={

            }
            devices_list=warnType.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 2  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(devices_list, request, self) # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = WarnTypeSerialiser(devices_list, many=True)
            jsondata={
            }
            jsondata['code']=20000
            # jsondata['total'] = page.page.paginator.count
            jsondata['items']=ret.data
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '告警类型获取失败'
            })


#编辑查询单个设备
class WarnType(APIView):
    # 获取单个告警类型
    def get(self,request,format='JSON'):
        user=request.user
        try:
            warntype_id = request.query_params['id']
            warntype=warnType.objects.get(id=warntype_id,user_id=user.id)
            serializer = WarnTypeSerialiser(warntype)
            response = {}
            response['data'] = serializer.data
            response['code'] = 20000
            return Response(response)
        except:
            return Response({
                'code': 0,
                'msg': '告警类型获取失败'
            })

    # 新增用户下单个告警类型
    def post(self, request):
        try:
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            ser = WarnTypeSerialiser(data=json_data)
            if ser.is_valid():
                ser.save()
                response={}
                response['data'] = ser.data
                response['code'] = 20000
                return Response(response)
            else:
                print(ser.errors)
                return Response(json.dumps(ser.errors))
        except:
            return Response({
                'code': 0,
                'msg': '数据写入失败'
            })

    # 删除单个设备信息
    def delete(self,request):
        user=request.user
        try:
            id=request.data['warntypeid']
            devices=warnType.objects.filter(id=id,warnFrom=1,user_id=user.id)
            devices.delete()
            jsondata={}
            jsondata['code']=20000
            jsondata['id']=id
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '数据删除失败'
            })

    # 修改单个设备信息
    def put(self,request):
        try:
            id = request.data['id']
            json_data = request.data.copy()
            json_data['user'] = request.user.id
            device = warnType.objects.get(id=id)
            ser = WarnTypeSerialiser(instance=device, data=json_data)
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

#获取告警数据列表
class WarnDataList(APIView):
    # 获取用户下设备列表
    def get(self,request,format="JSON"):
        user=request.user
        try:
            query_params=list(request.query_params.keys())
            kwargs={

            }
            kwargs['device__user_id']=user.id
            if 'sn' in query_params:
                kwargs['device__sn__contains'] = request.query_params['sn']

            if 'start' in query_params and request.query_params['start'] != '':
                kwargs['addtime__date__gte'] = request.query_params['start']
            if 'end' in query_params and request.query_params['end'] != '':
                kwargs['addtime__date__lte'] = request.query_params['end']
            if 'type' in query_params:
                kwargs['warnType_id'] = request.query_params['type']
            if 'name' in query_params :
                kwargs['device__name__contains'] = request.query_params['name']
            devices_list=warndata.objects.filter(**kwargs).order_by('-addtime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 2  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(devices_list, request, self) # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            ret = WarnDataSerializer(page_list, many=True)
            jsondata={
            }
            jsondata['code']=20000
            jsondata['total'] = page.page.paginator.count
            jsondata['items']=ret.data
            content = user.username + '进行获取告警列表操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '进行获取告警列表操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '告警列表获取失败'
            })

