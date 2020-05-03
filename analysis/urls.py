"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('devicedata/', views.deviceData.as_view()),   #获取用户下设备数据
    path('deviceparams/', views.deviceDaydata.as_view()),   #获取用户下设备
    path('deviceparamslist/', views.deviceDaydataList.as_view()),   #获取用户下设备
    path('devicerealtime/', views.deviceReal.as_view()),   #获取用户下设备数据# 数据
    path('powerdata/', views.powerData.as_view()),   #获取分组、楼层的实时总功率
    path('totaldata/', views.totalPower.as_view()),  # 用户实时总功率
    path('totalwarn/', views.totalWarn.as_view()),  # 用户实时总功率
    path('deviceType/', views.DeviceType.as_view()),  # 获取用户设备类型数据
    path('warnType/', views.WarnType.as_view()),  # 获取告警类型数据
    path('powerList/', views.TotalPower.as_view()),  #获取用户总功率历史
    path('eleList/', views.EleDataList.as_view()),  #获取本月内电量数据
    path('eleList_30/', views.EleDataList_30.as_view()),  #获取本月内电量数据
    path('groupPowerList/', views.GroupPowerData.as_view()),  #获取本月内电量数据
    path('buildPowerList/', views.BuildPowerData.as_view()),  #获取本月内电量数据
    path('buildTree/', views.BuildTree.as_view()),  #设备楼层分组树形结构
    # path('buildPowerList/', views.BuildPowerData.as_view()),  #获取本月内电量数据
    # path('buildingSingle/', views.buildingSingle.as_view()),  # 获取用户下设备类型占比
    # path('typeList/', views.typeList.as_view()),  # 类型列表
    # path('typeSingle/', views.typeSingle.as_view()),  # 类型信息
]

urlpatterns=format_suffix_patterns(urlpatterns)
