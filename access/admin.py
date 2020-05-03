from django.contrib import admin
from .models import *
# Register your models here.
class RealTimeDataAdmin(admin.ModelAdmin):
    list_display = ['device','meaEle','meaVol','tPower','meaHz','tEle','addTime','switchstate']
admin.site.register(RealTimeData,RealTimeDataAdmin)
