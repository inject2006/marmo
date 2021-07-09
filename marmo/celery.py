
# -*- coding:utf-8 -*-
# Author:wd
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marmo.settings')  # 设置django环境

celery_app = Celery('marmo')

celery_app.config_from_object('django.conf:settings', namespace='CELERY') #  使用CELERY_ 作为前缀，在settings中写配置

celery_app.autodiscover_tasks()  # 发现任务文件每个app下的task.py