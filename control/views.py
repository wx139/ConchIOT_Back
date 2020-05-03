from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from device.models import *
from django.http import FileResponse
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from access.tasks import *
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import requests
from logs.models import *

# Create your views here.
class deviceSetTime(APIView):
    def post(self,request,format="JSON"):
        user=request.user
        try:
            data=request.data
            device=Devices.objects.get(id=data['id'],user_id=user.id)
            if device:
                settime(device)
                content = user.username + '对设备进行校时操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response({
                    'code': 20000,
                    'msg': '校时成功'
                })
            else:
                content = user.username + '对设备进行校时操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response({
                    'code': 0,
                    'msg': '校时失败'
                })

        except:
            content = user.username + '对设备进行校时操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '校时失败'
            })


#设备单个设备的参数信息
class deviceParams(APIView):
    # 获取用户下设备列表
    def get(self,request,format="JSON"):
        user=request.user
        try:
            deviceid=request.query_params['deviceid']
            # getstate()
            device = Devices.objects.get(id=deviceid)
            getstate(device)
            deviceparams=DeviceParams.objects.filter(device__user_id=user.id,device__id=deviceid)
            if deviceparams.__len__()==0:
                jsondata = {}
                jsondata['code'] = 20000
                jsondata['data'] = {}
                return Response(jsondata)
            ser=ParamsSerialiser(deviceparams,many=True)
            ser.data[0]['kai1'] = getfromtime(ser.data[0]['kai1'])
            ser.data[0]['guan1'] = getfromtime(ser.data[0]['guan1'])
            ser.data[0]['kai2'] = getfromtime(ser.data[0]['kai2'])
            ser.data[0]['guan2'] = getfromtime(ser.data[0]['guan2'])
            ser.data[0]['chongfu'] = getchongfu(ser.data[0]['chongfu'])
            ser.data[0]['fz_01'] = get0data(ser.data[0]['fz_01'])
            print(ser.data[0])
            jsondata={}
            jsondata['code']=20000
            jsondata['data'] = ser.data[0]
            return Response(jsondata)
        except:
            return Response({
                'code': 0,
                'msg': '设备参数获取失败'
            })

    def post(self,request,format="JSON"):
        user=request.user
        try:
            data=request.data
            data['kai1']=setfromtime(data['kai1'])
            data['kai2'] = setfromtime(data['kai2'])
            data['guan1'] = setfromtime(data['guan1'])
            data['guan2'] = setfromtime(data['guan2'])
            data['chongfu'] = setchongfu(data['chongfu'])

            data['fz_01']= set0data(data['fz_01'])
            params = DeviceParams.objects.get(id=data['id'],device__user_id=user.id)
            ser = ParamsSerialiser(instance=params, data=data)
            if ser.is_valid():
                ser.save()
                senddata=data.copy()
                senddata['gldz'] = (hex(int(float(senddata['gldz']) * 10)).split('0x'))[1].zfill(4)
                senddata['zdgldz'] = (hex(int(float(senddata['zdgldz']) * 10)).split('0x'))[1].zfill(4)
                senddata['gdydz'] = (hex(int(float(senddata['gdydz']) * 10)).split('0x'))[1].zfill(4)
                senddata['ddydz'] = (hex(int(float(senddata['ddydz']) * 10)).split('0x'))[1].zfill(4)
                senddata['glys1'] = (hex(int(senddata['glys1'])).split('0x'))[1].zfill(4)
                senddata['glys2'] = (hex(int(senddata['glys2'])).split('0x'))[1].zfill(4)
                eleNum=0
                if (senddata['dfjg'] and senddata['yjdf']):
                    senddata = (float(senddata['yjdf']) / float(senddata['dfjg'])) * 100
                else:
                    eleNum = 0
                senddata['yjf'] = (hex(int(eleNum)).split('0x'))[1].zfill(8)
                dm = senddata['gldz'] + senddata['zdgldz'] + senddata['gdydz'] + senddata['ddydz'] + senddata['kai1'] + senddata['guan1'] + senddata['kai2'] + senddata['guan2'] + senddata['chongfu'] + senddata['glys1'] + senddata['glys2'] + senddata['yjf'] + senddata['fz_01']
                glkz(data['device']['sn'],data['device']['num'],dm)
                response = {}
                response['data'] = ser.data
                response['code'] = 20000
                content = user.username + '对设备进行设置参数操作；结果：成功！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(response)
            else:
                content = user.username + '对设备进行设置参数操作；结果：失败！'
                Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                    ip=request.META['REMOTE_ADDR'])
                return Response(ser.errors)
        except:
            content = user.username + '对设备进行设置参数操作；结果：失败！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '设备参数获取失败'
            })


#控制设备分控
class deviceControl(APIView):
    # 获取用户下设备列表
    def post(self,request,format="JSON"):
        user=request.user
        try:
            deviceids=request.data['deviceids']
            switch = request.data['switch']
            devices_list=Devices.objects.filter(user_id=user.id,id__in=deviceids)
            devices_data=DeviceListSerialiser(devices_list,many=True).data
            controlOnoff(devices_data,switch)
            jsondata={}
            jsondata['code']=20000
            jsondata['msg'] = '设备分合命令下发成功'
            tag=''
            if switch=='0':
                tag='分闸'
            else:
                tag='合闸'
            content = user.username + '对设备进行'+tag+'操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response(jsondata)
        except:
            content = user.username + '对设备进行控制操作；结果：成功！'
            Logs.objects.create(content=content, user=user, addtime=datetime.datetime.now(),
                                ip=request.META['REMOTE_ADDR'])
            return Response({
                'code': 0,
                'msg': '设备分合命令下发失败'
            })


def getfromtime(time):
    min1=time[0]+time[1]
    sec1=time[2]+time[3]
    hour1=time[6]+time[7]
    obj = {}
    obj['min']=int(min1,16)
    obj['sec']=int(sec1,16)
    obj['hour']=int(hour1,16)
    return obj

def getchongfu(chongfu):
    erjinzhi=bin(int(chongfu, 16)).split('0b')[1]
    backdata=erjinzhi.zfill(16)
    obj={}
    obj['chongfu1']={}
    obj['chongfu2'] = {}
    obj['chongfu2']['all']=gettf(backdata[0])
    obj['chongfu2']['周六']=gettf(backdata[1])
    obj['chongfu2']['周五']=gettf(backdata[2])
    obj['chongfu2']['周四']=gettf(backdata[3])
    obj['chongfu2']['周三'] = gettf(backdata[4])
    obj['chongfu2']['周二']=gettf(backdata[5])
    obj['chongfu2']['周一']=gettf(backdata[6])
    obj['chongfu2']['周日']=gettf(backdata[7])
    obj['chongfu1']['all'] = gettf(backdata[8])
    obj['chongfu1']['周六'] = gettf(backdata[9])
    obj['chongfu1']['周五'] = gettf(backdata[10])
    obj['chongfu1']['周四'] = gettf(backdata[11])
    obj['chongfu1']['周三'] = gettf(backdata[12])
    obj['chongfu1']['周二'] = gettf(backdata[13])
    obj['chongfu1']['周一'] = gettf(backdata[14])
    obj['chongfu1']['周日'] = gettf(backdata[15])
    return  obj


def get0data(fz0):
    erjinzhi = bin(int(fz0, 16)).split('0b')[1]
    backdata = erjinzhi.zfill(16)
    obj = {}
    obj['gdybh'] = gettf(backdata[15])
    obj['ddybh'] = gettf(backdata[14])
    obj['k1'] = gettf(backdata[13])
    obj['g1'] = gettf(backdata[12])
    obj['k2'] = gettf(backdata[11])
    obj['g2'] = gettf(backdata[10])
    obj['yjf'] = gettf(backdata[9])
    obj['kz1'] = gettf(backdata[8])
    obj['kz2'] = gettf(backdata[7])
    obj['wdgdz'] = gettf(backdata[6])
    obj['ycss'] = gettf(backdata[5])
    obj['jzds'] = gettf(backdata[4])
    obj['zzwgn'] = gettf(backdata[3])
    obj['ldbh'] = gettf(backdata[2])
    obj['xldhbh'] = gettf(backdata[1])
    obj['dnzl'] = gettf(backdata[0])

    return obj


def setfromtime(obj):
    min=(hex(int(obj['min'])).split('0x')[1]).zfill(2)
    sec=(hex(int(obj['sec'])).split('0x')[1]).zfill(2)
    hour = (hex(int(obj['hour'])).split('0x')[1]).zfill(2)
    backdata=min+sec+'00'+hour
    return backdata


def setchongfu(obj):
    backdata=[]
    backdata.append(settf(obj['chongfu2']['all']))
    backdata.append(settf(obj['chongfu2']['周六']))
    backdata.append(settf(obj['chongfu2']['周五']))
    backdata.append(settf(obj['chongfu2']['周四']))
    backdata.append(settf(obj['chongfu2']['周三']))
    backdata.append(settf(obj['chongfu2']['周二']))
    backdata.append(settf(obj['chongfu2']['周一']))
    backdata.append(settf(obj['chongfu2']['周日']))
    backdata.append(settf(obj['chongfu1']['all']))
    backdata.append(settf(obj['chongfu1']['周六']))
    backdata.append(settf(obj['chongfu1']['周五']))
    backdata.append(settf(obj['chongfu1']['周四']))
    backdata.append(settf(obj['chongfu1']['周三']))
    backdata.append(settf(obj['chongfu1']['周二']))
    backdata.append(settf(obj['chongfu1']['周一']))
    backdata.append(settf(obj['chongfu1']['周日']))
    str = ''.join(backdata)
    hexback=(hex(int(str, 2)).split('0x'))[1].zfill(4)
    return hexback


def set0data(obj):
    backdata = []
    backdata.append(settf(obj['dnzl']))
    backdata.append(settf(obj['xldhbh']))
    backdata.append(settf(obj['ldbh']))
    backdata.append(settf(obj['zzwgn']))
    backdata.append(settf(obj['jzds']))
    backdata.append(settf(obj['ycss']))
    backdata.append(settf(obj['wdgdz']))
    backdata.append(settf(obj['kz2']))
    backdata.append(settf(obj['kz1']))
    backdata.append(settf(obj['yjf']))
    backdata.append(settf(obj['g2']))
    backdata.append(settf(obj['k2']))
    backdata.append(settf(obj['g1']))
    backdata.append(settf(obj['k1']))
    backdata.append(settf(obj['ddybh']))
    backdata.append(settf(obj['gdybh']))
    str = ''.join(backdata)
    hexback = (hex(int(str, 2)).split('0x'))[1].zfill(4)
    return hexback

def settf(s):
    if(s==False):
        return '0'
    else:
        return '1'

