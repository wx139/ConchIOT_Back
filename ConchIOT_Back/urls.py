"""ConchIOT_Back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from access.views import *
from rest_framework.authtoken import views
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer,OpenAPIRenderer

schema_view = get_schema_view(title='API文档',renderer_classes=[OpenAPIRenderer,SwaggerUIRenderer])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('rbac.urls')),
    path('devicedata/',include('device.urls')),
    path('analysisdata/',include('analysis.urls')),
    path('warndata/',include('warndata.urls')),
    path('senddata/',include('control.urls')),
    path('log/',include('logs.urls')),
    path('docs/',schema_view,name='docs')
]
