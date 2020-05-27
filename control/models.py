from django.db import models

# Create your models here.
# 下发参数
class DeviceParams(models.Model):
    device = models.ForeignKey('device.Devices', related_name='params', verbose_name='参数管理', on_delete=models.CASCADE)
    kai1=models.CharField(max_length=32,verbose_name='定时1开时间',null=True,blank=True)
    guan1=models.CharField(max_length=32,verbose_name='定时1关时间',null=True,blank=True)
    kai2=models.CharField(max_length=32,verbose_name='定时2开时间',null=True,blank=True)
    guan2=models.CharField(max_length=32,verbose_name='定时2关时间',null=True,blank=True)
    chongfu=models.CharField(max_length=32,verbose_name='定时1开时间',null=True,blank=True)
    glys1 = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    glys2 = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    yjf = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    fz_01 = models.CharField(max_length=32, verbose_name='0区复制1',null=True,blank=True)
    fz_02 = models.CharField(max_length=32, verbose_name='0区复制2',null=True,blank=True)
    yjdf = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    dfjg = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    gldz = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    zdgldz = models.CharField(max_length=32, verbose_name='定时1开时间',null=True,blank=True)
    ddydz = models.CharField(max_length=32, verbose_name='低电压定值',null=True,blank=True)
    gdydz = models.CharField(max_length=32, verbose_name='过电压定值',null=True,blank=True)
    addtime=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '下发参数管理'
        verbose_name_plural = verbose_name