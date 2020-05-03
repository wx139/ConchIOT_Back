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
    path('warnTypeList/', views.WarnTypeList.as_view()),   #告警类型列表
    path('warnType/', views.WarnType.as_view()),   #告警类型操作
    path('warnDataList/', views.WarnDataList.as_view()),  # 告警数据列表
    # path('warnData/', views.groupSingle.as_view()),  # 告警
]

urlpatterns=format_suffix_patterns(urlpatterns)
