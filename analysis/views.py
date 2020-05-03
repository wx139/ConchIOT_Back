from django.shortcuts import render
from rest_framework.views import APIView
from access.models import *
from .serializers import *
from rest_framework.response import Response
import datetime
from device.models import *
from warndata.models import *
from datetime import timedelta
from django.db.models import Avg, Max, Min,Sum,Count
from rest_framework.pagination import PageNumberPagination
from access import tasks
from django.db.models.functions import TruncMonth, TruncYear,TruncDay

tasks.mqtt_run1()
# Create your views here.
# 获取用户下单个设备一天内实时数据
class deviceDaydata(APIView):
    def get(self, request, format="JSON"):
        user=request.user
        try:
            query_params = list(request.query_params.keys())
            kwargs = {
            }
            if 'deviceid' in query_params:
                kwargs['device__id'] = request.query_params['deviceid']
                kwargs['addTime__gte']=datetime.datetime.now().date()
            kwargs['device__user_id']=user.id
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            data_list = RealTimeData.objects.filter(**kwargs).order_by('-addTime')
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            # ret = GroupListSerialiser(page_list, many=True)
            ret = RealTimeListSerialiser(data_list, many=True)
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['items'] = ret.data
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备数据获取失败'
            })

class deviceDaydataList(APIView):
    def get(self, request, format="JSON"):
        user=request.user
        try:
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'deviceid' in query_params:
                kwargs['device__id'] = request.query_params['deviceid']
                kwargs['addTime__hour']=datetime.datetime.now().hour
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            kwargs['device__user_id']=user.id
            data_list = RealTimeData.objects.filter(**kwargs).order_by('-addTime')
            page = PageNumberPagination()  # 生成分页器对象
            page.page_size = 10  # 设置每页的条数
            page.page_query_param = 'page'  # url中查询第几页的key默认为'page
            page.page_size_query_param = 'limit'  # url中这一页数据的条数的key, 默认为None
            # page.max_page_size = 5  # 每页的最大数据条数

            page_list = page.paginate_queryset(data_list, request, self)  # 生成这一页的数据列表
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            # ret = GroupListSerialiser(page_list, many=True)
            ret = RealTimeListSerialiser(page_list, many=True)
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['items'] = ret.data
            jsondata['total'] = page.page.paginator.count
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备数据获取失败'
            })

# 获取用户设备总数和在线设备数量
class deviceData(APIView):
    def get(self, request, format="JSON"):
        user=request.user
        try:
            query_params = list(request.query_params.keys())
            kwargs = {}
            # if 'user' in query_params:
            kwargs['user__id'] = user.id
                # kwargs['addTime__hour']=datetime.datetime.now().hour
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            items={}
            refreshDataOnOff(user)
            devicetotal_count = Devices.objects.filter(user_id=user.id).count()
            deviceonline_count = Devices.objects.filter(status=1,user_id=user.id).count()
            items['devicetotal_count'] = devicetotal_count
            items['deviceonline_count'] = deviceonline_count
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['items'] = items
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备数据获取失败'
            })


# 获取单个设备实时数据最新
class deviceReal(APIView):
    def get(self, request, format="JSON"):
        user = request.user
        try:
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'deviceid' in query_params:
                kwargs['device__id'] = request.query_params['deviceid']
            kwargs['device__user_id']=user.id
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            data_list = ActualData.objects.filter(**kwargs)
            if data_list.__len__()>0:
                data_list=data_list[0]
                ret = ActualDataSerialiser(data_list)
            else:
                jsondata = {
                }
                jsondata['code'] = 20000
                jsondata['items'] = []
                return Response(jsondata)
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['items'] = ret.data
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备数据获取失败'
            })

#刷新用户在线设备和离线设备数据
class  refreshData(APIView):
    def get(self,request):
        user = request.user
        deviceonlineList = RealTimeData.objects.filter(
            addTime__gte=datetime.datetime.now() - timedelta(minutes=3),device__user_id=user.id).values(
            'device').distinct()
        devices_online = []
        devices_offline = []
        # 获取在线设备id
        for data in deviceonlineList:
            devices_online.append(str(data['device']))
        # 获取不在线设备
        deviceofflinelist = Devices.objects.exclude(id__in=devices_online)
        for data in deviceofflinelist:
            devices_offline.append(str(data.id))
        deviceofflinelist.update(status=0)
        Devices.objects.filter(id__in=devices_online).update(status=1)

# 获取分组、楼层的实时总功率
class powerData(APIView):
    def get(self,request):
        user=request.user
        query_params = list(request.query_params.keys())
        kwargs = {
             'addTime__gte': datetime.datetime.now() - timedelta(minutes=3)
        }
        if 'groupid' in query_params:
            kwargs['device__group_id'] = request.query_params['groupid']
        if 'buildingid' in query_params:
            kwargs['device__building_id'] = request.query_params['buildingid']
        kwargs['device__user_id'] = user.id
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data_list =ActualData.objects.filter(**kwargs).aggregate(power=Sum('tPower'))
        # ret = RealTimeListSerialiser(data_list, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data_list
        return Response(jsondata)

# 获取设备实时总功率
class totalPower(APIView):
    def get(self,request):
        user=request.user
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =ActualData.objects.filter(device__user_id=user.id).aggregate(power=Sum('tPower'))
        # ret = RealTimeListSerialiser(data_list, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取告警总数
class totalWarn(APIView):
    def get(self,request):
        user=request.user
        data=warndata.objects.filter(device__user=user).aggregate(count=Count('id'))
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取设备类型占比
class DeviceType(APIView):
    def get(self,request):
        user=request.user
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =Devices.objects.filter(user_id=user.id).values('type__name').annotate(Count('id'))
        # ret = RealTimeListSerialiser(data_list, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取告警类型占比
class WarnType(APIView):
    def get(self,request):
        user=request.user
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =warndata.objects.filter(device__user_id=user.id).values('warnType__warnname').annotate(Count('id'))
        # ret = RealTimeListSerialiser(data_list, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取一小时内实时功率数据
class TotalPower(APIView):
    def get(self,request):
        user=request.user
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =ActualDataTotal.objects.filter(user_id=user.id,addTime__gte=datetime.datetime.now() - timedelta(minutes=59))
        ret = ActualDataTotalSerialiser(data, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = ret.data
        return Response(jsondata)

# 获取本月用电量
class EleDataList(APIView):
    def get(self,request):
        user=request.user
        nowdate=datetime.datetime.now()
        data = DeviceHourDegree.objects.filter(addTime__year=nowdate.year,addTime__month=nowdate.month,device__user_id=user.id).annotate(
            days=TruncDay('addTime')).values('days').annotate(ele=Sum('ele'), pay=Sum('pay')).order_by('days')
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取30天内用电量
class EleDataList_30(APIView):
    def get(self,request):
        user=request.user
        cur_date=datetime.datetime.now()
        lastdate=cur_date-datetime.timedelta(days=30)
        print(lastdate)
        data = DeviceHourDegree.objects.filter(addTime__gt=lastdate,device__user_id=user.id).annotate(
            days=TruncDay('addTime')).values('days').annotate(ele=Sum('ele'), pay=Sum('pay')).order_by('days')
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取当前用户实时分组功率
class GroupPowerData(APIView):
    def get(self,request):
        user=request.user
        data=ActualData.objects.filter(device__user_id=user.id).values('device__group').annotate(power=Sum('tPower')).values('device__group__name','power').order_by('power')
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取当前用户实时楼层功率
class BuildPowerData(APIView):
    def get(self,request):
        user=request.user
        data = ActualData.objects.filter(device__user_id=user.id).values('device__building').annotate(power=Sum('tPower')).values(
            'device__building__name', 'power').order_by('power')
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)


class BuildTree(APIView):
    def get(self,request):
        user=request.user
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        nowdate=datetime.datetime.now()
        build = Buidling.objects.filter(user_id=user.id)
        ret = BuildSerialiser(build, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = ret.data
        return Response(jsondata)



#刷新用户在线设备和离线设备数据
def  refreshDataOnOff(user):
    deviceonlineList = RealTimeData.objects.filter(
        addTime__gte=datetime.datetime.now() - timedelta(minutes=3),device__user_id=user.id).values(
        'device').distinct()
    devices_online = []
    devices_offline = []
    # 获取在线设备id
    for data in deviceonlineList:
        devices_online.append(str(data['device']))
    # 获取不在线设备
    deviceofflinelist = Devices.objects.exclude(id__in=devices_online)
    for data in deviceofflinelist:
        devices_offline.append(str(data.id))
    deviceofflinelist.update(status=0)
    Devices.objects.filter(id__in=devices_online).update(status=1)