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
    path('deviceList/', views.deviceList.as_view()),   #设备列表
    path('deviceSingle/', views.deviceSingle.as_view()),   #设备信息
    path('groupList/', views.groupList.as_view()),  # 分组列表
    path('groupSingle/', views.groupSingle.as_view()),  # 分组信息
    path('buildingList/', views.buildingList.as_view()),  # 楼层列表
    path('buildingSingle/', views.buildingSingle.as_view()),  # 楼层信息
    path('typeList/', views.typeList.as_view()),  # 类型列表
    path('typeSingle/', views.typeSingle.as_view()),  # 类型信息
    path('downTempleate/', views.downTempleate.as_view()),  # 类型信息
]

urlpatterns=format_suffix_patterns(urlpatterns)
