# -*- coding:UTF-8 -*-
'''
    创建组件数据
'''
from app.models import MarmoProject
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()
from app.models import ComponentTag
class ComponentDao():
    def __init__(self):
        pass

    '''
        input:
        component_name,version,component_type,create_source,source_detail,project_name,description,asset
    '''
    def create_tag(self,data):
        try:
            project_name = data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    add_component_tag_params ={
                        "component_name":data["component_name"],
                        "version":data["version"],
                        "component_type": data["component_type"],
                        "create_source": data["create_source"],
                        "source_detail": data["source_detail"],
                        "project_id":int(project_id),
                        "description": data["description"],
                        "asset": data["asset"]
                    }
                    componet = ComponentTag.objects.create(**add_component_tag_params)
                    return True
        except Exception as e:
            raise Exception("创建组件失败=="+str(e.__str__()))


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


