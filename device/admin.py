from django.contrib import admin
from .models import *
# Register your models here.
class DevicesAdmin(admin.ModelAdmin):
    readonly_fields = ['building']

admin.site.register(Devices,DevicesAdmin)
admin.site.register(DeviceType)
admin.site.register(Group)
admin.site.register(Buidling)