from django.db import models

# Create your models here.
# 分组信息
class Logs(models.Model):
    content=models.CharField(max_length=500,verbose_name='日志内容',null=True,blank=True)
    user = models.ForeignKey('rbac.UserInfo', related_name='log', verbose_name='所属用户', on_delete=models.CASCADE)
    ip=models.CharField(max_length=32,verbose_name='IP',null=True,blank=True)
    addtime=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '日志管理'
        verbose_name_plural = verbose_name