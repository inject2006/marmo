from __future__ import absolute_import, unicode_literals
from .celery import celery_app as celery_app
import pymysql
pymysql.version_info =(1,4,13,"final",0)
pymysql.install_as_MySQLdb()
__all__ = ['celery_app']

