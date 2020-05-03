from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# class Menu(models.Model):
#     """
#     菜单
#     """
#     title=models.CharField(max_length=32,unique=True,verbose_name='菜单')
#     icon=models.CharField(max_length=10,verbose_name='菜单图标',null=True,blank=True)
#     url=models.CharField(max_length=100,verbose_name='菜单路径',null=True,blank=True)
#     parent=models.ForeignKey('Menu',null=True,blank=True,on_delete=models.CASCADE)
#     # 定义菜单间的自引用关系
#     # 权限url在菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段
#     # blank=True意味着后台管理中可以填写为空，根菜单没有父级权限
#
#     def __str__(self):
#         title_list=[self.title]
#         p=self.parent
#         while p:
#             title_list.insert(0,p.title)
#             p=p.parent
#         return '-'.join(title_list)
#
#     class Meta:
#         verbose_name='菜单'
#         verbose_name_plural=verbose_name

class Permission(models.Model):
    """
    权限
    """
    PERMISSION_TYPE=(
        ("0","菜单"),
        ("1","按钮")
    )
    title=models.CharField(max_length=32,unique=True,verbose_name='权限名称')
    url=models.CharField(max_length=128,unique=True,verbose_name='权限路径')
    type=models.CharField(max_length=1,choices=PERMISSION_TYPE)
    # menu=models.ForeignKey("Menu",null=True,blank=True,on_delete=models.CASCADE)
    parent = models.ForeignKey('Permission', null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return "{menu}---{permission}".format(menu=self.parent,permission=self.title)

    class Meta:
        verbose_name='权限'
        verbose_name_plural=verbose_name

class Role(models.Model):
    """
    角色：绑定权限
    """
    title=models.CharField(max_length=32,unique=True,verbose_name='角色')

    permissions=models.ManyToManyField("Permission")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name='角色'
        verbose_name_plural=verbose_name


class UserInfo(AbstractUser):
    """
    用户：划分角色
    """
    real_name=models.CharField(max_length=50,verbose_name='真实姓名',default='')
    mobile=models.CharField(max_length=11,null=True,blank=True,verbose_name="手机号码")
    roles=models.ManyToManyField(to="Role",verbose_name='角色')
    avatar=models.ImageField(verbose_name='用户图像',null=True,blank=True)
    dept=models.ForeignKey('Department',verbose_name='所属部门',on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        verbose_name='用户'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.username

class Department(models.Model):
    '''

    '''
    name=models.CharField(max_length=50,verbose_name='部门名称',default='')
    description=models.CharField(max_length=500,null=True,blank=True,verbose_name="部门简介")
    parent = models.ForeignKey('Department', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name='部门'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name