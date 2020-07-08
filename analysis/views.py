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
from rbac.models import *

tasks.mqtt_run1()
# Create your views here.

def getDept(id,depts,dept_arr):
    for dept in depts:
        if dept.parent and dept.parent.id==id:
            dept_arr.append(dept.id)
            dept_arr=(getDept(dept.id,depts,dept_arr))
    return dept_arr

# 获取用户下单个设备一天内实时数据
class deviceDaydata(APIView):
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
            if 'deviceid' in query_params:
                kwargs['device__id'] = request.query_params['deviceid']
                kwargs['addTime__gte']=datetime.datetime.now().date()
            kwargs['device__user__dept_id__in']=dept_arr
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            data_list = RealTimeData.objects.filter(**kwargs).order_by('-addTime')
            tag=Devices.objects.get(id=request.query_params['deviceid']).type.tag
            if tag=='3':
                ret = RealTimeListSerialiser_WL(data_list, many=True)
            else:
                ret = RealTimeListSerialiser(data_list, many=True)
            # page_list.
            # 将这一页的数据列表序列化
            # return Response(ret.data)  # 返回查到的数据列表
            # ret = GroupListSerialiser(page_list, many=True)


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
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'deviceid' in query_params:
                kwargs['device__id'] = request.query_params['deviceid']
                kwargs['addTime__hour']=datetime.datetime.now().hour
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            kwargs['device__user__dept_id__in']=dept_arr
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
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {}
            # if 'user' in query_params:
            kwargs['user__id'] = user.id
                # kwargs['addTime__hour']=datetime.datetime.now().hour
            # if 'name' in query_params:
            #     kwargs['name__contains'] = request.query_params['name']
            items={}
            refreshDataOnOff(user)
            devicetotal_count = Devices.objects.filter(user__dept_id__in=dept_arr).count()
            deviceonline_count = Devices.objects.filter(status=1,user__dept_id__in=dept_arr).count()
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
            dept_id = user.dept.id
            dept_arr = []
            depts = Department.objects.all()
            getDept(dept_id, depts, dept_arr).append(dept_id)
            query_params = list(request.query_params.keys())
            kwargs = {

            }
            if 'deviceid' in query_params:
                kwargs['device__id'] = request.query_params['deviceid']
            kwargs['device__user__dept_id__in']=dept_arr
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        deviceonlineList = RealTimeData.objects.filter(
            addTime__gte=datetime.datetime.now() - timedelta(minutes=3),device__user__dept_id__in=dept_arr).values(
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        query_params = list(request.query_params.keys())
        kwargs = {
             'addTime__gte': datetime.datetime.now() - timedelta(minutes=3)
        }
        if 'groupid' in query_params:
            kwargs['device__group_id'] = request.query_params['groupid']
        if 'buildingid' in query_params:
            kwargs['device__building_id'] = request.query_params['buildingid']
        kwargs['device__user__dept_id__in'] = dept_arr
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =ActualData.objects.filter(addTime__gte=datetime.datetime.now() - timedelta(minutes=3),device__user__dept_id__in=dept_arr).aggregate(power=Sum('tPower'))
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        data=warndata.objects.filter(device__user__dept_id__in=dept_arr).aggregate(count=Count('id'))
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取设备类型占比
class DeviceType(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =Devices.objects.filter(user__dept_id__in=dept_arr).values('type__name').annotate(Count('id'))
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =warndata.objects.filter(device__user__dept_id__in=dept_arr).values('warnType__warnname').annotate(Count('id'))
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        data =ActualDataTotal.objects.filter(user__dept_id__in=dept_arr,addTime__gte=datetime.datetime.now() - timedelta(minutes=59))
        ret = ActualDataTotalSerialiser(data, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = ret.data
        return Response(jsondata)

# 获取规定时间内楼层功率数据
class TotalPowerBuild(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        query_params = list(request.query_params.keys())
        kwargs = {

        }
        if 'start' in query_params and request.query_params['start'] != '':
            kwargs['addTime__date__gte'] = request.query_params['start']
        else:
            kwargs['addTime__date__gte'] = datetime.datetime.now() - timedelta(minutes=59)
        if 'end' in query_params and request.query_params['end'] != '':
            kwargs['addTime__date__lte'] = request.query_params['end']
        else:
            kwargs['addTime__date__lte'] = datetime.datetime.now()
        kwargs['build__id'] = request.query_params['buildid']
        kwargs['addTime__minute'] = 0
        data =ActualDataBuild.objects.filter(**kwargs)
        ret = ActualDataBuildSerialiser(data, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = ret.data
        return Response(jsondata)

# 获取规定时间内功率数据
class TotalPowerGroup(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        query_params = list(request.query_params.keys())
        kwargs = {

        }
        if 'sn' in query_params:
            kwargs['sn__contains'] = request.query_params['sn']
        if 'group' in query_params and request.query_params['group'] != '':
            kwargs['group__id'] = request.query_params['group']
        if 'building' in query_params and request.query_params['building'] != '':
            kwargs['building__id'] = request.query_params['building']
        if 'type' in query_params and request.query_params['type'] != '':
            kwargs['type__id'] = request.query_params['type']
        if 'name' in query_params:
            kwargs['name__contains'] = request.query_params['name']
        kwargs['user__dept_id__in'] = dept_arr
        data =ActualDataTotal.objects.filter(user__dept_id__in=dept_arr,addTime__gte=datetime.datetime.now() - timedelta(minutes=59))
        ret = ActualDataTotalSerialiser(data, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = ret.data
        return Response(jsondata)


# 获取规定时间内功率数据
class TotalPowerDevice(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        query_params = list(request.query_params.keys())
        kwargs = {

        }
        if 'sn' in query_params:
            kwargs['sn__contains'] = request.query_params['sn']
        if 'group' in query_params and request.query_params['group'] != '':
            kwargs['group__id'] = request.query_params['group']
        if 'building' in query_params and request.query_params['building'] != '':
            kwargs['building__id'] = request.query_params['building']
        if 'type' in query_params and request.query_params['type'] != '':
            kwargs['type__id'] = request.query_params['type']
        if 'name' in query_params:
            kwargs['name__contains'] = request.query_params['name']
        kwargs['user__dept_id__in'] = dept_arr
        data =ActualDataTotal.objects.filter(user__dept_id__in=dept_arr,addTime__gte=datetime.datetime.now() - timedelta(minutes=59))
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        nowdate=datetime.datetime.now()
        data = DeviceHourDegree.objects.filter(addTime__year=nowdate.year,addTime__month=nowdate.month,device__user__dept_id__in=dept_arr).annotate(
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        cur_date=datetime.datetime.now()
        lastdate=cur_date-datetime.timedelta(days=30)
        print(lastdate)
        data = DeviceHourDegree.objects.filter(addTime__gt=lastdate,device__user__dept_id__in=dept_arr).annotate(
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
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        data=ActualData.objects.filter(device__user__dept_id__in=dept_arr).values('device__group').annotate(power=Sum('tPower')).values('device__group__name','power').order_by('power')
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)

# 获取当前用户实时楼层功率
class BuildPowerData(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        data = ActualData.objects.filter(device__user__dept_id__in=dept_arr).values('device__building').annotate(power=Sum('tPower')).values(
            'device__building__name', 'power').order_by('power')
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = data
        return Response(jsondata)


class BuildTree(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        # if 'name' in query_params:
        #     kwargs['name__contains'] = request.query_params['name']
        nowdate=datetime.datetime.now()
        provinces=Buidling.objects.values('province').filter(user__dept_id__in=dept_arr).distinct()
        devices=Devices.objects.filter(user__dept_id__in=dept_arr)
        deviceData=DeviceSerializer(devices,many=True)
        province_list=[]
        for province in provinces:
            pro={
                'name':province['province'],
                'children':[]
            }
            citys=Buidling.objects.values('city').filter(province=province['province']).distinct()
            for city in citys:
                city_obj={
                    'name':city['city'],
                    'children':[],
                }
                pro['children'].append(city_obj)
                areas=Buidling.objects.values('area').filter(city=city['city']).distinct()
                for area in areas:
                    area_obj={
                        'name':area['area'],
                        'children':[]

                    }
                    build=Buidling.objects.filter(user__dept_id__in=dept_arr,area=area['area'])
                    ret = BuildSerialiser(build, many=True)
                    area_obj['children']=ret.data
                    city_obj['children'].append(area_obj)

            # print(citys)
            province_list.append(pro)
        print(province_list)
        # build = Buidling.objects.filter(user_id=user.id)
        # ret = BuildSerialiser(build, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = province_list
        jsondata['devices']=deviceData.data
        return Response(jsondata)


class BuildTreeBb(APIView):
    def get(self,request):
        user=request.user
        dept_id = user.dept.id
        dept_arr = []
        depts = Department.objects.all()
        getDept(dept_id, depts, dept_arr).append(dept_id)
        build = Buidling.objects.filter(user__dept_id__in=dept_arr)
        ret = BuildSerialiser(build, many=True)
        jsondata = {
        }
        jsondata['code'] = 20000
        jsondata['items'] = ret.data
        return Response(jsondata)



#刷新用户在线设备和离线设备数据
def  refreshDataOnOff(user):
    dept_id = user.dept.id
    dept_arr = []
    depts = Department.objects.all()
    getDept(dept_id, depts, dept_arr).append(dept_id)
    deviceonlineList = RealTimeData.objects.filter(
        addTime__gte=datetime.datetime.now() - timedelta(minutes=3),device__user__dept_id__in=dept_arr).values(
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





# 统计分析

class PowerList(APIView):
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
            devices_list=ActualDataTotal.objects.filter(**kwargs)
            data = ActualDataTotal.objects.filter(user__dept_id__in=dept_arr,
                                                  addTime__gte=datetime.datetime.now() - timedelta(minutes=59))
            ret = ActualDataTotalSerialiser(data, many=True)
            jsondata = {
            }
            jsondata['code'] = 20000
            jsondata['items'] = ret.data
            return Response(jsondata)
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