#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name redisworker
__time__ = "2021/6/10 14:57"
from django_redis import get_redis_connection
from marmo.settings import TASK_LIST
from celery.result import AsyncResult
from app.dao.module_function import ModuleFunctionDao
import json
import time
'''
    redis任务调度器
    功能:从redis队列中获取任务是否执行完毕，如果执行完毕则修改任务状态,否则任务重新入库
'''
from threading import Thread
class WorkRedisThread(Thread):
    def __init__(self):
        super(Thread).__init__()


    def run(self):
        connection = get_redis_connection("default")
        modulefunctiondao = ModuleFunctionDao()
        while True:
            try:
                if connection.llen(TASK_LIST) >0:
                    task_id = connection.rpop(TASK_LIST)
                    if task_id:
                        task_result = AsyncResult(id=task_id)
                        is_ready =task_result.ready()
                        state = task_result.state
                        if is_ready and state =="SUCCESS":
                            result = task_result.result
                            if result:
                                result = json.loads(result)
                                asset_id =""
                                project_id =""
                                module_name=""
                                asset_type=""
                                if result.__contains__("asset_id"):
                                    asset_id=result["asset_id"]
                                if result.__contains__("project_id"):
                                    project_id=result["project_id"]
                                if result.__contains__("asset_type"):
                                    asset_type=result["asset_type"]
                                if result.__contains__("module_name"):
                                    module_name=result["module_name"]
                                if asset_id and project_id and module_name and asset_type:
                                    update_params ={
                                        "asset_id":asset_id,
                                        "project_id":project_id,
                                        "asset_type":asset_type,
                                        "module_name":module_name
                                    }
                                    if result.__contains__["exists_data"]:
                                        exists_data = result["exists_data"]
                                        if exists_data: #存在数据
                                            update_params["module_log"]=result["data"]
                                        else:
                                            update_params["module_log"]=""
                                    if result.__contains__["status_code"]:
                                        status_code = result["status_code"]
                                        if status_code ==3:
                                            update_params["fail_reason"]=result["fail_reason"]
                                        update_params["module_status"]=status_code
                                    modulefunctiondao.update_module_function(update_params)
                        else:
                           connection.lpush(TASK_LIST,task_id)
                time.sleep(0.5)
            except Exception as e:
                print("获取任务结果出现异常=="+str(e.__str__()))
                continue
























