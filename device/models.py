from django.db import models
# Create your models here.
# 楼层信息
class Buidling(models.Model):
    name=models.CharField(max_length=32,verbose_name='楼层名称')
    icon=models.ImageField(verbose_name='楼层图片', null=True, blank=True)
    remarks=models.CharField(max_length=500,verbose_name='备注',null=True,blank=True)
    user=models.ForeignKey('rbac.UserInfo',related_name='building',verbose_name='所属用户',on_delete=models.CASCADE)
    addtime=models.DateTimeField(auto_now=True)
    province=models.CharField(max_length=32,verbose_name='省',null=True,blank=True)
    city=models.CharField(max_length=32,verbose_name='市',null=True,blank=True)
    area=models.CharField(max_length=32,verbose_name='区',null=True,blank=True)
    address=models.CharField(max_length=200,verbose_name='地址',null=True,blank=True)
    lng = models.FloatField(verbose_name='经度', null=True, blank=True)
    lat = models.FloatField(verbose_name='纬度', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '楼层管理'
        verbose_name_plural = verbose_name

# 分组信息
class Group(models.Model):
    name=models.CharField(max_length=32,verbose_name='分组名称')
    icon=models.ImageField(verbose_name='分组图片', null=True, blank=True)
    remarks=models.CharField(max_length=500,verbose_name='备注',null=True,blank=True)
    user = models.ForeignKey('rbac.UserInfo', related_name='group', verbose_name='所属用户', on_delete=models.CASCADE)
    building = models.ForeignKey('Buidling', related_name='group', verbose_name='所属楼层', on_delete=models.CASCADE)
    addtime=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分组管理'
        verbose_name_plural = verbose_name

# 设备类型
class DeviceType(models.Model):
    TYPE_STATUS = (
        ('0', 'stateraw'),
        ('1', 'state'),
    )
    name=models.CharField(max_length=32,verbose_name='设备类型名称')
    icon=models.ImageField(verbose_name='设备类型图片', null=True, blank=True)
    remarks=models.CharField(max_length=500,verbose_name='备注',null=True,blank=True)
    tag=models.CharField(default='0',choices=TYPE_STATUS,verbose_name='订阅方式',max_length=1)
    addtime=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '类型管理'
        verbose_name_plural = verbose_name

# 设备信息
class Devices(models.Model):
    TYPE_STATUS = (
        ('1', '在线'),
        ('0', '离线'),
    )
    TYPE_SWITCH = (
        ('1', '打开'),
        ('0', '关闭'),
    )
    name=models.CharField(max_length=32,verbose_name='设备名称',db_index=True)
    sn=models.CharField(max_length=64,verbose_name='设备网关编码',db_index=True)
    num=models.CharField(max_length=32,verbose_name='设备地址位')
    type=models.ForeignKey('DeviceType',related_name='device',verbose_name='设备类型',on_delete=models.CASCADE)
    lng=models.FloatField(verbose_name='经度', null=True, blank=True)
    lat=models.FloatField(verbose_name='纬度', null=True, blank=True)
    address=models.CharField(max_length=100,verbose_name='设备地址', null=True, blank=True)
    group=models.ForeignKey('Group',related_name='device',verbose_name='所属分组',on_delete=models.CASCADE)
    building = models.ForeignKey('Buidling', related_name='device', verbose_name='所属楼层', on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey('rbac.UserInfo', related_name='device', verbose_name='所属用户', on_delete=models.CASCADE)
    addtime=models.DateTimeField(auto_now=True)
    status=models.CharField(max_length=50,choices=TYPE_STATUS,verbose_name='在离线状态',default=0)
    switch=models.CharField(max_length=50,choices=TYPE_SWITCH,verbose_name='开关状态',default=0)
    remarks = models.CharField(max_length=500, verbose_name='备注', null=True, blank=True)
    param1 = models.CharField(max_length=50,verbose_name='备用参数1',null=True,blank=True)
    param2 = models.CharField(max_length=50, verbose_name='备用参数2', null=True, blank=True)
    param3 = models.CharField(max_length=50, verbose_name='备用参数3', null=True, blank=True)
    param4 = models.CharField(max_length=50, verbose_name='备用参数4', null=True, blank=True)
    param5 = models.CharField(max_length=50, verbose_name='备用参数5', null=True, blank=True)
    param6 = models.CharField(max_length=50, verbose_name='备用参数6', null=True, blank=True)
    param7 = models.CharField(max_length=50, verbose_name='备用参数7', null=True, blank=True)
    param8 = models.CharField(max_length=50, verbose_name='备用参数8', null=True, blank=True)
    param9 = models.CharField(max_length=50, verbose_name='备用参数9', null=True, blank=True)
    param10 = models.CharField(max_length=50, verbose_name='备用参数10', null=True, blank=True)
    param11 = models.CharField(max_length=50, verbose_name='备用参数11', null=True, blank=True)


    def save(self,*args,**kwargs):
        self.building=self.group.building
        super(Devices, self).save(*args, **kwargs)


    def __str__(self):
        return self.name+'---'+self.sn

    class Meta:
        verbose_name = '设备管理'
        verbose_name_plural = verbose_name


# 设备参数
class Parms(models.Model):
    name=models.CharField(max_length=50,verbose_name='参数名')
    key=models.CharField(max_length=50,verbose_name='参数key')
    value=models.CharField(max_length=50,verbose_name='参数值')
    remarks=models.CharField(max_length=500,verbose_name='备注',null=True,blank=True)
    is_system=models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '参数管理'
        verbose_name_plural = verbose_name
