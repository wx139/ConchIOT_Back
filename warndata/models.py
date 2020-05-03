from django.db import models

# Create your models here.
# 告警数据
class warndata(models.Model):

    device=models.ForeignKey('device.Devices',related_name='warndata',verbose_name='设备信息',on_delete=models.CASCADE)
    addtime = models.DateTimeField(auto_now=True,verbose_name='告警时间')
    warnEle = models.FloatField('告警时电流信息', null=True, blank=True)  # 电流
    warnVol = models.FloatField('告警时电压信息', null=True, blank=True)  # 电压
    warnPower = models.FloatField('告警时功率信息', null=True, blank=True)  # 功率
    warnHz = models.FloatField('告警时频率', null=True, blank=True)  # 频率
    warntEle = models.FloatField('告警时有功电度量', null=True, blank=True)  # 有功电度量Ω
    warnpEle = models.FloatField('告警时漏电流', null=True, blank=True)  # 漏电流
    warnType =models.ForeignKey('warnType',related_name='warndata',on_delete=models.CASCADE,verbose_name='告警类型')

# 自定义告警类型
class warnType(models.Model):
    WARN_TYPE = (
        ('0', '设备主动告警'),
        ('1', '系统设置告警')
    )

    PARAMS_TYPE = (
        ('0', '电压'),
        ('1', '电流'),
        ('2', '功率'),
        ('3', '电度量'),
        ('4', '频率'),
    )
    warnname=models.CharField('告警类型名称',max_length=50)
    warnAddr=models.IntegerField('主动告警标示位',null=True,blank=True)
    warnFrom=models.CharField(choices=WARN_TYPE,verbose_name='告警来源',max_length=32)
    uplimit=models.FloatField('系统告警上限阀值',null=True,blank=True)
    downlimit=models.FloatField('系统告警下限阀值',null=True,blank=True)
    is_able=models.BooleanField(default=False,verbose_name='是否启用')
    user=models.ForeignKey('rbac.UserInfo',related_name='warntype',on_delete=models.CASCADE,verbose_name='用户',null=True,blank=True)
    addtime = models.DateTimeField(auto_now=True, verbose_name='添加时间')


