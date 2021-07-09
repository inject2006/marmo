# -*- coding:UTF-8 -*-
from app.models import ModuleFunction,MarmoProject
import os
import json
from app.utils.marmo_logger import Marmo_Logger
from app.exceptions.module_exception import ModuleException
logger = Marmo_Logger()
class ModuleFunctionDao():
    def __init__(self):
        pass

    '''
       input:
       module_name,asset_type,asset_id,project_id
    '''
    def insert_module_function(self,data):
        try:
            asset_id = data["asset_id"]
            project_id = data["project_id"]
            module_name = data["module_name"]
            asset_type = data["asset_type"]
            module_status =0
            if asset_id and project_id and asset_type and module_status:
                module_function = ModuleFunction(asset_id=int(asset_id),project_id=int(project_id),module_name=module_name,module_status=module_status,asset_type=asset_type)
                module_function.save()
                return True
            else:
                raise Exception("module function 缺少关键参数")
        except Exception as e:
            logger.log("insert module_function 出现异常"+str(e.__str__()))
            return False

    '''
        更新module_function的状态
        有project_id就行，project_name不一定用
    '''
    def update_module_function(self,data):
        try:
            project_id =""
            if not data.__contains__("project_id"):
                project_name = data["project_name"]
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
            else:
                project_id = data["project_id"]
            asset_id = data["asset_id"]
            module_name = data["module_name"]
            asset_type = data["asset_type"]
            module_log = data["module_log"]
            module_status=data["module_status"]
            if data.__contains__("fail_reason"):
                fail_reason =data["fail_reason"]
            else:
                fail_reason =""
            if asset_id and project_id and module_name and asset_type:
                module_function = ModuleFunction.objects.filter(asset_id=int(asset_id),project_id=int(project_id),module_name=module_name,asset_type=asset_type).get()
                if module_function:
                    module_function.module_log=module_log
                    module_function.module_status=module_status
                    if fail_reason:
                        module_function.fail_reason=fail_reason
                    module_function.save()
            else:
                raise ModuleException("更新模块状态参数不完整 %s,%s,%s,%s"%(str(asset_id),str(project_id),str(module_name),str(asset_type)))
        except ModuleFunction.DoesNotExist:
            raise Exception("要更新的模块功能不存在")
        except ModuleException as me:
            raise ModuleException(me)
        except Exception as e:
            logger.log("更新模块功能状态异常"+str(e.__str__()))
            raise Exception("更新模块功能状态异常"+str(e.__str__()))

    '''
              根据项目名称查询项目是否存在
          '''

    def query_project_exists_by_name(self, project_name):
        assert project_name
        try:
            project_obj = MarmoProject.objects.filter(name=project_name).get()
            return project_obj
        except MarmoProject.DoesNotExist:
            logger.log("新增域名项目不存在")
            raise Exception("新增域名项目不存在")
        except Exception as e:
            logger.log("query project exists " + str(e.__str__()))
            raise Exception("query project exists " + str(e.__str__()))





