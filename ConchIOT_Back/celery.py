from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ConchIOT_Back.settings')  # 设置django环境

app = Celery('ConchIOT_Back')

app.config_from_object('django.conf:settings', namespace='CELERY') #  使用CELERY_ 作为前缀，在settings中写配置

app.conf.update(
    # 定时任务
    CELERYBEAT_SCHEDULE={
        'add-every-30-seconds': {
            'task': 'access.tasks.dataServer',  # 将实时数据统计电量储存
            'schedule': crontab(minute=57, hour='*/1'),  # 每小时的57分执行一次任务
            'args': ()
        },
        'add-every-3-seconds': {
            'task': 'access.tasks.dataServer',  # 离线判断，每3分钟执行
            'schedule': crontab(minute="*/3"),  # 每3分种执行一次任务
            'args': ()
        },
        'add-every-3-m': {
            'task': 'access.tasks.dataPower',  # 设备功率率统计
            'schedule': crontab(minute="*/1"),  # 每1分分组执行一次任务
            'args': ()
        },
        'getallparams': {
            'task': 'access.tasks.getstateAll',  # 设备功率率统计
            'schedule': crontab(minute=55, hour='*/1'),  # 每小时的57分执行一次任务
            'args': ()
        }

    }
)

app.autodiscover_tasks()