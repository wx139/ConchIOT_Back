from __future__ import absolute_import, unicode_literals
from device.models import *
from .models import *
from celery import shared_task
import paho.mqtt.client as mqtt
import re
import datetime
from datetime import timedelta
from .models import *
from control.models import *
from pycrc.CRC16 import CRC16
from django.db.models import Avg, Max, Min,Sum,Count
from warndata.models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# 引入mqtt包
# import paho.mqtt.client as mqtt
# 使用独立线程运行
from threading import Thread
# from .tasks import *
import re
import time
import json
from celery.result import AsyncResult
from datetime import timedelta
from django.db.models.functions import TruncMinute,TruncDay


# 自定义模型查询，有返回一个，没有返回None
def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
#CRC验证码校验
def getcrc(crcdm):
    target = bytes().fromhex(crcdm)
    crc = "{:4X}".format(
        CRC16(modbus_flag=True).calculate(target))
    crc = (crc[2:4] + crc[0:2]).replace(" ","0")
    crcdm = crcdm + crc
    return crcdm

#100系列报文标示
n_meaVol_100=9
n_meaEle_100=11
n_tPower_100=13
n_nPower_100=17
n_meaHz_100=21
n_tEle_100=23
n_nEle_100=27
n_pEle_100=31
n_state_100=33
n_active_100=35
n_newThing_100=37
n_stateEqu_100=39
n_snum_100=41
n_errornum_100=43
n_copy1_100=45
n_copy2_100=47

#300系列+WL报文标示
n_Ltemp_300=3
n_Ntemp_300=5
n_Ctemp_300=7
n_meaVol_300=9
n_meaEle_300=11
n_tPower_300=13
n_nPower_300=17
n_meaHz_300=21
n_tEle_300=23
n_nEle_300=27
n_pEle_300=49
n_state_300=33
n_copy1_300=35
n_copy2_300=37
n_stateEqu_300=39
n_snum_300=41
n_errornum_300=43
n_copy1_300=35
n_copy2_300=47


def gettf(s):
    if(s=='0'):
        return False
    else:
        return True


def getwarn(device,code,meaEle,tEle,meaVol,pEle,tPower,meaHz):
    erjinzhi = bin(int(code, 16)).split('0b')[1]
    backdata = erjinzhi.zfill(16)
    gjbsdata={}
    mes = ''
    if(gettf(backdata[14])==True):
        # mes=mes+'过电压告警;'
        # gjbsdata[0]='1'
        warntype = warnType.objects.get(id=5)
        warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle,warnpEle=pEle, warnVol=meaVol,
                                warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)
    if (gettf(backdata[13]) == True):
        mes = mes + '低电压告警;'
        # gjbsdata[1] = '1'
        warntype = warnType.objects.get(id=6)
        warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle, warnpEle=pEle,warnVol=meaVol,
                                warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)
    if (gettf(backdata[12]) == True):
         mes = mes + '过流动作;'
         # gjbsdata[2] = '1'
         warntype = warnType.objects.get(id=7)
         warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle,warnpEle=pEle, warnVol=meaVol,
                                 warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)
    if (gettf(backdata[6]) == True):
        mes = mes + '过流告警;'
        # gjbsdata[3] = '1'
        warntype = warnType.objects.get(id=9)
        warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle,warnpEle=pEle, warnVol=meaVol,
                                warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)
    if (gettf(backdata[5]) == True):
        mes = mes + '过温告警;'
        # gjbsdata[4] = '1'
        warntype = warnType.objects.get(id=11)
        warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle,warnpEle=pEle, warnVol=meaVol,
                                warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)
    if (gettf(backdata[4]) == True):
        mes = mes + '剩余电量不足<10度;'
        # gjbsdata[5] = '1'
        warntype = warnType.objects.get(id=13)
        warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle,warnpEle=pEle, warnVol=meaVol,
                                warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)
    if (gettf(backdata[3]) == True):
        mes = mes + '通讯异常;'
        # gjbsdata[6] = '1'
        warntype = warnType.objects.get(id=54)
        warndata.objects.create(device=device, addtime=datetime.datetime.now(), warnEle=meaEle,warnpEle=pEle, warnVol=meaVol,
                                warnPower=tPower, warnHz=meaHz, warntEle=tEle,warnType=warntype)

# 将实时数据存储到持久化数据库中
@shared_task
def data_in_mysql_modbus(sn,data):
    pattern = re.compile('.{1,2}')
    s = ' '.join(pattern.findall(data))
    # 转换16进制数据
    datas = s.split(' ')
    # 获取设备地址位
    addr = datas[0].lstrip('0')
    # 获取控制位
    ctrnum =datas[1]
    device = None
    try:
        device = Devices.objects.get(sn=sn,num=addr)
    except Devices.DoesNotExist:
        return None
    if device:
        if ctrnum == '03':
            print(ctrnum)
            try:
                gldz = str(int((datas[3] + datas[4]), 16) * 0.1)
                zdgldz = str(int((datas[5] + datas[6]), 16) * 0.1)
                gdydz = str(int((datas[7] + datas[8]), 16) * 0.1)
                ddydz = str(int((datas[9] + datas[10]), 16) * 0.1)
                kai1 = str(datas[11] + datas[12] + datas[13] + datas[14])
                guan1 = str(datas[15] + datas[16] + datas[17] + datas[18])
                kai2 = str(datas[19] + datas[20] + datas[21] + datas[22])
                guan2 = str(datas[23] + datas[24] + datas[25] + datas[26])
                chongfu = str(datas[27] + datas[28])
                ys1 = str(int((datas[29] + datas[30]), 16))
                ys2 = str(int((datas[31] + datas[32]), 16))
                yjf = str(int((datas[35] + datas[36] + datas[33] + datas[34]), 16) * 0.01)
                fz0_1 = str(datas[37] + datas[38])
                fz0_2 = str(datas[39] + datas[40])
                print('过流定值:' + datas[3] + datas[4])
                print('最大过流定值:' + datas[5] + datas[6])
                print('定时开1:' + datas[8] + datas[12] + datas[13] + datas[14])
                print('定时关1:' + datas[15] + datas[16] + datas[17] + datas[18])
                print('定时开2:' + datas[19] + datas[20] + datas[21] + datas[22])
                print('定时关2:' + datas[23] + datas[24] + datas[25] + datas[26])
                print('重复功能:' + datas[27] + datas[28])
                print('功率预设1:' + datas[29] + datas[30])
                print('功率预设2:' + datas[31] + datas[32])
                print('预交费定值:' + str(yjf))
                print('预交费定值2:' + datas[33] + datas[34] + datas[35] + datas[36])
                print('0区复制1:' + datas[37] + datas[38])
                print('0区复制2:' + datas[39] + datas[40])
                print(device.id)
                DeviceParams.objects.update_or_create(device__id=device.id,
                                                  defaults={'device': device, 'kai1': kai1, 'guan1': guan1,
                                                            'kai2': kai2, 'guan2': guan2, 'chongfu': chongfu,
                                                            'yjf': yjf, 'fz_01': fz0_1, 'fz_02': fz0_2,
                                                            'gldz':gldz,
                                                            'zdgldz':zdgldz, 'gdydz': gdydz, 'ddydz': ddydz,
                                                            'glys1': ys1, 'glys2': ys2,
                                                            'addtime': datetime.datetime.now()})
            except:
                pass
        elif ctrnum == '04':
            if device.type.tag=='0':
                modbus100(device,datas)
            elif device.type.tag=='1':
                modbus300(device,datas)

        # getwaring(warnstring,device)
            # except:
            #     pass

@shared_task
def data_in_mysql_json(sn,data):
    try:
        devicedata = data['subdevice']
        addr = devicedata['addr'][0]
        device= Devices.objects.get(sn=sn,num=addr)
    except :
        return None
    if device:
        try:
            device.switch = devicedata['output']
            device.lng = data['lng']
            device.lat = data['lat']
            device.save()
            RealTimeData.objects.create(device=device, meaEle=devicedata['cur'][0], meaHz=devicedata['freq'][0], meaVol=devicedata['vol'][0],tEle=devicedata['ele'][0], tPower=devicedata['power'][0],
                                        switchstate=devicedata['output'], addTime=datetime.datetime.now(),params1=devicedata['temp'][0],params2=devicedata['temp1'][0],params3=devicedata['ctemp'][0])
            ActualData.objects.update_or_create(device__id=device.id,
                                                defaults={'device': device, 'meaEle': devicedata['cur'][0], 'tEle': devicedata['ele'][0],
                                                          'meaHz': devicedata['freq'][0], 'meaVol': devicedata['vol'][0],
                                                          'tPower': devicedata['power'][0], 'switchstate': devicedata['output'],
                                                          'addTime': datetime.datetime.now(),'params1':devicedata['temp'][0],'params2':devicedata['temp1'][0],'params3':devicedata['ctemp'][0]})
        except:
            pass

# 定时任务，每小时执行，将实时数据统计电量储存
@shared_task()
def dataServer():
    dataList = RealTimeData.objects.filter(addTime__gte=datetime.datetime.now().date(),
                                           addTime__hour=datetime.datetime.now().hour).values(
        'device').distinct().annotate(ele=Max('tEle') - Min('tEle'))
    for data in dataList:
        DeviceHourDegree.objects.create(device_id=data['device'], ele=data['ele'], addTime=datetime.datetime.now())


# 定时任务，离线判断，每*分钟执行
@shared_task()
def dataOnline():
    # 查询3分钟内有数据的设备
    deviceonlineList = RealTimeData.objects.filter(addTime__gte=datetime.datetime.now() - timedelta(minutes=3)).values(
        'device').distinct()
    devices_online = []
    devices_offline=[]
    # 获取在线设备id
    for data in deviceonlineList:
        devices_online.append(str(data['device']))
    # 获取不在线设备
    deviceofflinelist=Devices.objects.exclude(id__in=devices_online)
    for data in deviceofflinelist:
        devices_offline.append(str(data['device']))
    deviceofflinelist.update(status=0)
    deviceonlineList.update(status=1)

# 定时任务，设备功率率统计
@shared_task()
def dataPower():
    devicepowerList = ActualData.objects.filter(addTime__gte=datetime.datetime.now() - timedelta(minutes=3)).values(
        'device__user').annotate(Sum('tPower'))
    deivepowerL = []
    grouppowerL = []
    buildpowerL = []
    for devicepower in devicepowerList:
        obj = ActualDataTotal(user_id=devicepower['device__user'], totalPower=devicepower['tPower__sum'],
                              addTime=datetime.datetime.now())
        deivepowerL.append(obj)

    grouppowerList = ActualData.objects.filter(addTime__gte=datetime.datetime.now() - timedelta(minutes=3)).values(
        'device__group').annotate(Sum('tPower'))
    for grouppower in grouppowerList:
        obj = ActualDataGroup(group_id=grouppower['device__group'], totalPower=grouppower['tPower__sum'],
                              addTime=datetime.datetime.now())
        grouppowerL.append(obj)

    buildpowerList = ActualData.objects.filter(addTime__gte=datetime.datetime.now() - timedelta(minutes=3)).values(
        'device__building').annotate(Sum('tPower'))
    for buildpower in buildpowerList:
        obj = ActualDataBuild(build_id=buildpower['device__building'], totalPower=buildpower['tPower__sum'],
                              addTime=datetime.datetime.now())
        buildpowerL.append(obj)
    ActualDataTotal.objects.bulk_create(deivepowerL, batch_size=100)
    ActualDataGroup.objects.bulk_create(grouppowerL, batch_size=100)
    ActualDataBuild.objects.bulk_create(buildpowerL, batch_size=100)


# 控制设备分合
@shared_task()
def controlOnoff(devicelist,switch):
    for device in devicelist:
        dyh=''
        if(device['type']['tag']=='0'):
            dyh = device['sn'] + 'ctrraw'
        else:
            dyh = device['sn'] + 'ctr'
        dm = ''
        if (len(device['num']) < 2):
            device['num'] = '0' + device['num']
        if (switch == '1'):
            dm = device['num'] + '06000455AA'
            crcdm = getcrc(dm).replace(" ","0")
        else:
            dm = device['num'] + '06000455CC'
            crcdm = getcrc(dm).replace(" ","0")
        client.subscribe(dyh)
        client.publish(dyh, bytearray.fromhex(crcdm))
        time.sleep(0.5)
        # client.loop_start()

# 进行空开内部校时
@shared_task()
def settime(device):
    dyh = device.sn + 'ctrraw'
    timenow = datetime.datetime.now()
    nian = hex(timenow.year).split('0x')[1].zfill(4)
    yue = hex(timenow.month).split('0x')[1].zfill(4)
    weekday = timenow.weekday() + 1
    if (weekday == 7):
        weekday = 0
    week = hex(weekday).split('0x')[1].zfill(4)
    day = hex(timenow.day).split('0x')[1].zfill(4)
    hour = hex(timenow.hour).split('0x')[1].zfill(4)
    min = hex(timenow.minute).split('0x')[1].zfill(4)
    sec = hex(timenow.second).split('0x')[1].zfill(4)
    hm = '0000'
    dm = nian + yue + week + day + hour + min + sec + hm
    if len(device.num)==1:
        device.num="0"+device.num
    sdm = device.num + '10 00 05 00 08 10' + dm
    crcdm = getcrc(sdm.replace(" ",""))
    client.subscribe(dyh)
    client.publish(dyh, bytearray.fromhex(crcdm))
    # client.loop_start()

@shared_task()
def getstate(device):
    if (len(device.num) < 2):
        device.num = '0' + device.num
    state=''
    ctr=''
    dm = device.num + '0300110013'
    if (device.type.tag == '0'):
        state = device.sn + 'stateraw'
        ctr =  device.sn + 'ctrraw'
    else:
        state = device.sn + 'state'
        ctr = device.sn + 'ctr'
    try:
        crcdm = getcrc(dm).replace(" ",'0')
        client.subscribe(state)
        client.publish(ctr, bytearray.fromhex(crcdm))
    except:
        pass

@shared_task()
def glkz(device,dm):
    if (len(device.num) < 2):
        device.num = '0' + device.num
    dyh=''
    if (device.type.tag == '0'):
        dyh =  device.sn + 'ctrraw'
    else:
        dyh = device.sn + 'ctr'
    sdm=device.num+'100011001326'+dm
    crcdm=getcrc(sdm)
    client.subscribe(dyh)
    client.publish(dyh, bytearray.fromhex(crcdm))


@shared_task()
def getstateAll():
    devicelist=Devices.objects.all()
    for device in devicelist:
        getstate.delay(device)

# 建立mqtt连接
def on_connect(client, userdata, flag, rc):
    print("已经连接上控驰服务器" + str(rc))


# 接收、处理mqtt消息
def on_message(client, userdata, msg):
    # out = str(msg.payload.decode('utf-8'))
    data = bytearray.hex(bytearray(msg.payload))
    matchtopic_state=re.match('.*state$',msg.topic)
    matchtopic_stateraw = re.match('.*stateraw$', msg.topic)
    if matchtopic_stateraw:
        data = bytearray.hex(bytearray(msg.payload))
        sn=msg.topic.split('stateraw')[0]
        data_in_mysql_modbus.delay(sn,data)
    if matchtopic_state:
        try:
            data = json.loads(str(msg.payload.decode('utf-8')))
            sn = msg.topic.split('state')[0]
            data_in_mysql_json.delay(sn, data)
        except:
            pass
        try:
            data = bytearray.hex(bytearray(msg.payload))
            sn = msg.topic.split('state')[0]
            data_in_mysql_modbus.delay(sn, data)
        except:
            pass



# mqtt客户端启动函数
def mqttfunction():
    global client
    # 使用loop_start 可以避免阻塞Django进程，使用loop_forever()可能会阻塞系统进程
    client.loop_start()
    # client.loop_forever() 有掉线重连功能
    # client.loop_forever(retry_first_connection=True)


client = mqtt.Client(clean_session=True)

# 启动函数
def mqtt_run1():
    print('启动函数')
    client.on_connect = on_connect
    client.on_message = on_message
    # 绑定 MQTT 服务器地址
    broker = '47.97.105.3'
    # broker = '47.93.220.133'
    # MQTT服务器的端口号
    client.connect(broker, 1883, 60)
    client.subscribe("#")
    # client.reconnect_delay_set(min_delay=1, max_delay=2000)
    # 启动
    mqttthread = Thread(target=mqttfunction)
    mqttthread.start()
    # pass



def modbus100(device,datas):
    Bnum = int(datas[2], 16)
    meaVol = int(datas[n_meaVol_100] + datas[n_meaVol_100 + 1], 16) * 0.1
    meaEle = int(datas[n_meaEle_100] + datas[n_meaEle_100 + 1], 16) * 0.01
    tPower = int(datas[n_tPower_100] + datas[n_tPower_100 + 1] + datas[n_tPower_100 + 2] + datas[n_tPower_100 + 3], 16) * 0.1
    nPower = int(datas[n_nPower_100] + datas[n_nPower_100 + 1] + datas[n_nPower_100 + 2] + datas[n_nPower_100 + 3], 16) * 0.1
    meaHz = int(datas[n_meaHz_100] + datas[n_meaHz_100+ 1], 16) * 0.01
    tEle = int(datas[n_tEle_100]+ datas[n_tEle_100 + 1] + datas[n_tEle_100 + 2] + datas[n_tEle_100 + 3], 16) * 0.01
    nEle = int(datas[n_nEle_100] + datas[n_nEle_100+ 1] + datas[n_nEle_100 + 2] + datas[n_nEle_100 + 3], 16) * 0.01
    pEle = int(datas[n_pEle_100] + datas[n_pEle_100 + 1], 16) * 1.0
    state = int(datas[n_state_100] + datas[n_state_100 + 1], 16)
    active = int(datas[n_active_100] + datas[n_active_100 + 1], 16)
    newThing = int(datas[n_newThing_100] + datas[n_newThing_100 + 1], 16)
    stateEqu = int(datas[n_stateEqu_100] + datas[n_stateEqu_100 + 1], 16)
    sNum = int(datas[n_snum_100] + datas[n_snum_100 + 1], 16)
    errornum = int(datas[n_errornum_100] + datas[n_errornum_100 + 1], 16)
    warnstring = str(datas[n_copy1_100]) + str(datas[n_copy1_100 + 1])
    getwarn(device, warnstring, meaEle, tEle, meaVol, pEle, tPower, meaHz)
    device.switch = state
    device.save()
    actual = ActualData.objects.filter(device__id=device.id)
    if actual.__len__() > 1:
        actual[0].delete()
    RealTimeData.objects.create(device=device, meaEle=meaEle, tEle=tEle, meaHz=meaHz, meaVol=meaVol, pEle=pEle,
                                tPower=tPower, switchstate=state, addTime=datetime.datetime.now())
    ActualData.objects.update_or_create(device__id=device.id,
                                        defaults={'device': device, 'meaEle': meaEle, 'tEle': tEle,
                                                  'meaHz': meaHz, 'meaVol': meaVol, 'pEle': pEle,
                                                  'tPower': tPower, 'switchstate': state,
                                                  'addTime': datetime.datetime.now()})

def modbus300(device,datas):
    Bnum = int(datas[2], 16)
    temp_L = int(datas[n_Ltemp_300] + datas[n_Ltemp_300 + 1], 16) * 0.1
    temp_N = int(datas[n_Ntemp_300] + datas[n_Ntemp_300 + 1], 16) * 0.01
    temp_C = int(datas[n_Ctemp_300] + datas[n_Ctemp_300 + 1], 16) * 0.1
    meaVol = int(datas[n_meaVol_300] + datas[n_meaVol_300 + 1], 16) * 0.1
    meaEle = int(datas[n_meaEle_300] + datas[n_meaEle_300 + 1], 16) * 0.01
    tPower = int(datas[n_tPower_300] + datas[n_tPower_300 + 1] + datas[n_tPower_300 + 2] + datas[n_tPower_300 + 3], 16) * 0.1
    nPower = int(datas[n_nPower_300] + datas[n_nPower_300 + 1] + datas[n_nPower_300 + 2] + datas[n_nPower_300 + 3], 16) * 0.1
    meaHz = int(datas[n_meaHz_300] + datas[n_meaHz_300 + 1], 16) * 0.01
    tEle = int(datas[n_tEle_300] + datas[n_tEle_300 + 1] + datas[n_tEle_300 + 2] + datas[n_tEle_300 + 3], 16) * 0.01
    nEle = int(datas[n_nEle_300] + datas[n_nEle_300 + 1] + datas[n_nEle_300 + 2] + datas[n_nEle_300 + 3], 16) * 0.01
    pEle = int(datas[n_pEle_300] + datas[n_pEle_300 + 1], 16) * 1.0
    state = int(datas[n_state_300] + datas[n_state_300 + 1], 16)
    stateEqu = int(datas[n_stateEqu_300] + datas[n_stateEqu_300 + 1], 16)
    sNum = int(datas[n_snum_300] + datas[n_snum_300 + 1], 16)
    errornum = int(datas[n_errornum_300] + datas[n_errornum_300 + 1], 16)
    warnstring = str(datas[n_copy1_300]) + str(datas[n_copy1_300 + 1])
    getwarn(device, warnstring, meaEle, tEle, meaVol, pEle, tPower, meaHz)
    device.switch = state
    device.save()
    actual = ActualData.objects.filter(device__id=device.id)
    if actual.__len__() > 1:
        actual[0].delete()
    RealTimeData.objects.create(device=device, meaEle=meaEle, tEle=tEle, meaHz=meaHz, meaVol=meaVol, pEle=pEle,
                                tPower=tPower, switchstate=state, addTime=datetime.datetime.now(), params1=temp_L,
                                params2=temp_N, params3=temp_C)
    ActualData.objects.update_or_create(device__id=device.id,
                                        defaults={'device': device, 'meaEle': meaEle, 'tEle': tEle,
                                                  'meaHz': meaHz, 'meaVol': meaVol, 'pEle': pEle,
                                                  'tPower': tPower, 'switchstate': state,
                                                  'addTime': datetime.datetime.now(), 'params1': temp_L,
                                                  'params2': temp_N, 'params3': temp_C})

