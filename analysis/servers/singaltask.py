from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from device.models import *
from analysis.models import *

@receiver(post_save, sender=Devices)
def my_handler(sender, **kwargs):
    userid=kwargs['instance'].user_id
    devices=Devices.objects.filter(user__id=userid).count()
    online=Devices.objects.filter(user__id=userid,switch='1').count()
