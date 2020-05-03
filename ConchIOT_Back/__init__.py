from __future__ import absolute_import,unicode_literals
from .celery import app as celery_app
import pymysql
# from access import datainput

__all___=['celery_app']
pymysql.install_as_MySQLdb()
# datainput.mqtt_run()