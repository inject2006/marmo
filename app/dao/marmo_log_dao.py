#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name marmo_log_dao
__time__ = "2021/6/15 11:10"

from app.models import MarmoLog
class MarmoLogDao():
    def __init__(self):
        pass

    def add_log(self,data):
        try:
            assert data["module"]
            assert data["module_log"]
            assert data["type"]
            assert data["asset_id"]
            add_params ={
                "module":data["module"],
                "type":data["type"],
                "module_log":data["module_log"],
                "asset_id":data["asset_id"]
            }
            log_obj = MarmoLog.objects.create(**add_params)
            if log_obj:
                return True
            else:
                raise Exception("新增日志出现错误")
        except Exception as e:
            print("add log error=="+str(e.__str__()))
            raise Exception("add log error=="+str(e.__str__()))
