# -*- coding:UTF-8 -*-
'''
    旁站dao
'''
from django.db import connection
from app.models import SideStations,MarmoProject,OnlineAssetIp
import json
from datetime import datetime
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class SideStaionsDao():
    def __init__(self):
        pass

    '''
        插入旁站数据
    '''
    def insert_side_station(self,data):
        try:
            info = data["info"]
            asset_id = data["asset_id"]
            project_id =data["project_id"]
            if info and asset_id and project_id:
                side_stations = SideStations(info=info,asset_id=asset_id,project_id=project_id)
                side_stations.save()
                return True
            else:
                raise Exception("插入旁站数据参数不全")
        except Exception as e:
            logger.log("insert side station error="+str(e.__str__()))
            raise Exception("insert side station error="+str(e.__str__()))


    '''
        查询旁站
        input:
        asset_id,project_id
    '''
    def query_side_stations(self,data):
        try:
            result_list =[]
            project_name=""
            ip=""
            if data.__contains__("project_name"):
                project_name =data["project_name"]
            if data.__contains__("ip"):
                ip =data["ip"]

            if project_name and ip:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    '''
                        查询ip对应的id
                    '''
                    asset_obj =OnlineAssetIp.objects.filter(project_id=project_id,ip=ip).get()
                    if asset_obj:
                        asset_id =asset_obj.id
                        stations_list =SideStations.objects.filter(asset_id=int(asset_id),project_id=int(project_id))[:]
                        for stations in stations_list:
                            info = stations.info
                            info_json =json.loads(info)
                            station_obj ={}
                            station_obj["title"]=info_json["title"]
                            station_obj["host"]=info_json["host"]
                            station_obj["create_time"]=stations.create_time
                            result_list.append(station_obj)
                return result_list
            else:
                raise Exception("查询旁站参数异常")
        except Exception as e:
            logger.log("query side station error="+str(e.__str__()))
            raise Exception("query side station error="+str(e.__str__()))

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





