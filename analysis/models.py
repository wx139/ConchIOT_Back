from django.db import models

# Create your models here.
# 当前用户设备信息统计
class DevicesCount(models.Model):
    user=models.ForeignKey('rbac.UserInfo',related_name='devicecount', verbose_name='所属用户', on_delete=models.CASCADE)
    all_count=models.BigIntegerField(verbose_name='设备总数',null=True,blank=True)
    online_count=models.BigIntegerField(verbose_name='在线总数',null=True,blank=True)
    power=models.FloatField('总功率',null=True,blank=True)

    # warn_count=models.BigIntegerField(verbose_name='故障设备数')

# #楼层数据
# class BuildingData(models.Model):
#     device=models.ForeignKey('device.Devices',related_name='buildingdata',verbose_name='实时数据',on_delete=models.CASCADE)
#
