from ..models import UserInfo
import json
from ..serializers import *

def init_permission(request,user_obj):
    """
    初始化用户权限，写入session
    :param request:
    :param user_obj:
    :return:
    """
    # 获取当前角色的功能权限

    permission_item_list=(list(user_obj.roles.values('permissions__url',
                                               'permissions__title',
                                               'permissions__type',
                                               'permissions__parent').distinct()))

    # print(permission_item_list)
    #获取当前用户角色关联的菜单ID
    permission_menu_list1=list(user_obj.roles.values_list('permissions__parent',flat=True).distinct())

    # menu=Menu.objects.filter(id__in=permission_menu_list1)
    menu_list=[]
    # print(menu)
    # for item in menu:
    #     if item.parent_id:
    #         menu_parent=Menu.objects.get(id=item.parent_id)
    #         menu_item=MenuSerializer(menu_parent).data
    #         menu_list.append(menu_item)
    #     menu_item=Menu.objects.get(id=item.id)
    #     menu_list.append(MenuSerializer(menu_item).data)
    # print(menu_list)
    backdata={}
    backdata['menu']=menu_list
    backdata['permission']=permission_item_list
    print(backdata)

    return backdata
    permission_url_list=[]  #用户权限url列表，--->用于中间件验证用户权限
    permission_menu_list=[] #用户权限url所属菜单列表

    # for item in permission_menu_list1: # print(permission_item_list)
    # # print(menu_list)
    # #     permission_url_list.append(item['permissions__url'])
    #     if item['permissions__menu_id']:
    #         menu_item=Menu.objects.filter(parent_id__in=permission_menu_list1)
    #         print(menu_item)
    #         # temp={"title":item['permissions__title'],
    #         #       "url":item['permissions__url'],
    #         #       "menu_id":item['permissions__menu_id'],
    #         #       }
    #         # permission_menu_list.append(temp)
    #
    # menu_list=list(Menu.objects.values('id','title','parent_id','icon'))
    #注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session,加list()转为可序列化对象

    from django.conf import  settings

    # request.session[settings.SESSION_PERMISSSION_URL_KEY]=permission_url_list

    # request.session[settings.SESSION_MENU_KEY]={
    #     settings.ALL_MENU_KEY:menu_list,
    #     settings.PERMISSION_MENU_KEY:permission_menu_list,
    # }