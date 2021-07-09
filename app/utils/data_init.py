#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name data_init
__time__ = "2021/6/23 10:15"
from django.db import connection
from django_redis import get_redis_connection
class DataInit():
    def __init__(self):
        self.cursor =connection.cursor()
        self.redis_connection = get_redis_connection("default")

    '''
        初始化redis数据
    '''
    def init_redis(self):
        pass


