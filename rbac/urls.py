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
    path('login/', views.LoginView.as_view()),   #用户登录
    path('logout/', views.LogoutView.as_view()),   #用户登出
    path('register/', views.RegisterView.as_view()),   #用户注册
    path('info/', views.UserInfoSet.as_view()),        #获取当前用户信息
    path('getinfo/', views.GetInfo.as_view()),        #测试Token验证
    path('permission/', views.PermissionView.as_view()),  #获取用户权限
    path('userList/', views.userList.as_view()),           #获取用户列表
    path('userSingle/', views.userSingle.as_view()),   #用户信息
    path('roleList/', views.roleList.as_view()),           #获取角色列表
    path('roleSingle/', views.roleSingle.as_view()),   #角色信息
    path('powerList/', views.powerList.as_view()),           #获取权限列表
    path('powerSingle/', views.powerSingle.as_view()),   #角色信息
    path('orgList/', views.orgList.as_view()),           #获取权限列表
    path('orgSingle/', views.orgSingle.as_view()),   #角色信息
]

urlpatterns=format_suffix_patterns(urlpatterns)
