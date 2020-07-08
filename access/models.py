from django.db import models
# Create your models here.
# 实时数据信息
class RealTimeData(models.Model):
    SWITCH_TYPE=(
        (0,'合闸'),
        (1, '分闸')
    )
    device=models.ForeignKey('device.Devices',related_name='realtimedata',verbose_name='实时数据',on_delete=models.CASCADE)
    addTime = models.DateTimeField('上报时间')
    meaEle = models.FloatField('电流',null=True,blank=True)  # 电流
    meaVol = models.FloatField('电压',null=True,blank=True)  # 电压
    tPower = models.FloatField('功率',null=True,blank=True)  # 功率
    meaHz = models.FloatField('频率',null=True,blank=True)  # 频率
    tEle = models.FloatField('有功电度量',null=True,blank=True)  # 有功电度量
    pEle = models.FloatField('漏电流',null=True,blank=True)  # 漏电流
    params1 = models.FloatField('备用参数1',null=True,blank=True)  # 漏电流
    params2 = models.FloatField('备用参数2',null=True,blank=True)  # 漏电流
    params3 = models.FloatField('备用参数3',null=True,blank=True)  # 漏电流
    params4 = models.FloatField('备用参数4',null=True,blank=True)  # 漏电流
    params5 = models.FloatField('备用参数5',null=True,blank=True)  # 漏电流
    params6 = models.FloatField('备用参数6',null=True,blank=True)  # 漏电流
    params7 = models.FloatField('备用参数7',null=True,blank=True)  # 漏电流
    params8 = models.FloatField('备用参数8',null=True,blank=True)  # 漏电流
    params9 = models.FloatField('备用参数9',null=True,blank=True)  # 漏电流
    params10 = models.FloatField('备用参数10',null=True,blank=True)  # 漏电流
    params11 = models.FloatField('备用参数11',null=True,blank=True)  # 漏电流
    params12 = models.FloatField('备用参数12',null=True,blank=True)  # 漏电流
    params13 = models.FloatField('备用参数13',null=True,blank=True)  # 漏电流
    params14 = models.FloatField('备用参数4', null=True, blank=True)  # 漏电流
    params15 = models.FloatField('备用参数5', null=True, blank=True)  # 漏电流
    params16 = models.FloatField('备用参数6', null=True, blank=True)  # 漏电流
    params17 = models.FloatField('备用参数7', null=True, blank=True)  # 漏电流
    params18 = models.FloatField('备用参数8', null=True, blank=True)  # 漏电流
    params19 = models.FloatField('备用参数9', null=True, blank=True)  # 漏电流
    params20 = models.FloatField('备用参数10', null=True, blank=True)  # 漏电流

    switchstate = models.IntegerField(choices=SWITCH_TYPE,verbose_name='设备开关状态')  # 设备开关状态

    class Meta:
        verbose_name = '实时历史数据'
        verbose_name_plural = verbose_name

# 设备每小时电度量
class DeviceHourDegree(models.Model):
    device=models.ForeignKey('device.Devices',related_name='devicehourdegree',verbose_name='设备每小时电度量',on_delete=models.CASCADE)
    addTime = models.DateTimeField('计算时间')
    ele = models.FloatField('电量', null=True, blank=True)  # 有功电度量
    pay= models.FloatField('电费', null=True, blank=True)  # 有功电度量
    class Meta:
        verbose_name='每小时电度量'
        verbose_name_plural=verbose_name


# 分组每小时电度量、电费
class GroupHourDegree(models.Model):
    device=models.ForeignKey('device.Group',related_name='grouphourdegree',verbose_name='分组每小时电度量',on_delete=models.CASCADE)
    addTime = models.DateTimeField('计算时间')
    tEle = models.FloatField('有功电度量', null=True, blank=True)  # 有功电度量
    pay= models.FloatField('电费', null=True, blank=True)  # 有功电度量
    class Meta:
        verbose_name='每小时电度量'
        verbose_name_plural=verbose_name

# 分组每小时电度量、电费
class BuildingHourDegree(models.Model):
    device=models.ForeignKey('device.Buidling',related_name='buildinghourdegree',verbose_name='楼层每小时电度量',on_delete=models.CASCADE)
    addTime = models.DateTimeField('计算时间')
    tEle = models.FloatField('有功电度量', null=True, blank=True)  # 有功电度量
    pay= models.FloatField('电费', null=True, blank=True)  # 有功电度量
    class Meta:
        verbose_name='每小时电度量'
        verbose_name_plural=verbose_name

# #分组功率记录
# class GroupPower(models.Model):
#     device = models.ForeignKey('device.Group', related_name='grouphourdegree', verbose_name='分组每小时电度量',
#                                on_delete=models.CASCADE)
#     addTime = models.DateTimeField('计算时间')
#     tEle = models.FloatField('功率', null=True, blank=True)  # 有功电度量
#     pay = models.FloatField('电费', null=True, blank=True)  # 有功电度量
#
#     class Meta:
#         verbose_name = '每小时电度量'
#         verbose_name_plural = verbose_name


class ActualData(models.Model):
    SWITCH_TYPE=(
        (0,'合闸'),
        (1, '分闸')
    )
    device=models.ForeignKey('device.Devices',related_name='actualdatahistory',verbose_name='实时历史数据',on_delete=models.CASCADE)
    addTime = models.DateTimeField('上报时间')
    meaEle = models.FloatField('电流',null=True,blank=True)  # 电流
    meaVol = models.FloatField('电压',null=True,blank=True)  # 电压
    tPower = models.FloatField('功率',null=True,blank=True)  # 功率
    meaHz = models.FloatField('频率',null=True,blank=True)  # 频率
    tEle = models.FloatField('有功电度量',null=True,blank=True)  # 有功电度量
    pEle = models.FloatField('漏电流',null=True,blank=True)  # 漏电流
    params1 = models.FloatField('备用参数1',null=True,blank=True)  # 漏电流
    params2 = models.FloatField('备用参数2',null=True,blank=True)  # 漏电流
    params3 = models.FloatField('备用参数3',null=True,blank=True)  # 漏电流
    params4 = models.FloatField('备用参数4',null=True,blank=True)  # 漏电流
    params5 = models.FloatField('备用参数5',null=True,blank=True)  # 漏电流
    params6 = models.FloatField('备用参数6',null=True,blank=True)  # 漏电流
    params7 = models.FloatField('备用参数7',null=True,blank=True)  # 漏电流
    params8 = models.FloatField('备用参数8',null=True,blank=True)  # 漏电流
    params9 = models.FloatField('备用参数9',null=True,blank=True)  # 漏电流
    params10 = models.FloatField('备用参数10',null=True,blank=True)  # 漏电流
    params11 = models.FloatField('备用参数11',null=True,blank=True)  # 漏电流
    params12 = models.FloatField('备用参数12',null=True,blank=True)  # 漏电流
    params13 = models.FloatField('备用参数13',null=True,blank=True)  # 漏电流
    params14 = models.FloatField('备用参数4', null=True, blank=True)  # 漏电流
    params15 = models.FloatField('备用参数5', null=True, blank=True)  # 漏电流
    params16 = models.FloatField('备用参数6', null=True, blank=True)  # 漏电流
    params17 = models.FloatField('备用参数7', null=True, blank=True)  # 漏电流
    params18 = models.FloatField('备用参数8', null=True, blank=True)  # 漏电流
    params19 = models.FloatField('备用参数9', null=True, blank=True)  # 漏电流
    params20 = models.FloatField('备用参数10', null=True, blank=True)  # 漏电流

    switchstate = models.IntegerField(choices=SWITCH_TYPE,verbose_name='设备开关状态')  # 设备开关状态

    class Meta:
        verbose_name = '实时数据'
        verbose_name_plural = verbose_name


# 每个用户每分钟功率统计
class ActualDataTotal(models.Model):
    user = models.ForeignKey('rbac.UserInfo', related_name='actualdatatotal', verbose_name='所属用户', on_delete=models.CASCADE)
    totalPower=models.BigIntegerField('总功率')
    addTime = models.DateTimeField('统计时间')

    class Meta:
        verbose_name = '用户功率统计'
        verbose_name_plural = verbose_name

# 楼层每分钟功率统计
class ActualDataBuild(models.Model):
    build = models.ForeignKey('device.Buidling', related_name='actualdatabuild', verbose_name='所属楼层', on_delete=models.CASCADE)
    totalPower=models.BigIntegerField('总功率')
    addTime = models.DateTimeField('统计时间')

    class Meta:
        verbose_name = '楼层功率统计'
        verbose_name_plural = verbose_name

# 楼层每分钟功率统计
class ActualDataGroup(models.Model):
    group = models.ForeignKey('device.Group', related_name='actualdatagroup', verbose_name='所属分组', on_delete=models.CASCADE)
    totalPower=models.BigIntegerField('总功率')
    addTime = models.DateTimeField('统计时间')

    class Meta:
        verbose_name = '分组功率统计'
        verbose_name_plural = verbose_name