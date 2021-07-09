# -*- coding:UTF-8 -*-
'''
    banner探测模块
    一次只探测一个端口
    文件名格式:ip_port.xml
'''
import os
from xml.dom.minidom import parse
from app.dao.service_dao import ServiceDao
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
from marmo.settings import PORTBANNERFILEPATH,PORTBANNER_COMMAND
class PortBanner():
    def __init__(self,asset_data):
        self.asset_data =asset_data
        self.port = asset_data["port"]
        self.command =PORTBANNER_COMMAND
        self.ip =asset_data["asset"]
        self.file_path=PORTBANNERFILEPATH
        self.file_name=str(self.ip)+"_"+str(self.port)+".xml"
        self.banner =""
        self.version=""
        self.description=""
        self.module_name=asset_data["module_name"]
        self.data_info = {
            "exists_data": False,
            "status_code": 2,
            "fail_reason": "",
            "data": "",
            "module_name": self.module_name,
            "asset_type": asset_data["asset_type"],
            "asset_id": asset_data["asset_id"],
            "project_id": asset_data["project_id"],
            "project_name": asset_data["project_name"]
        }
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }
        self.exists_data =False

    '''
        执行nmap端口扫描
    '''
    def run_command(self):
        # try:
        if not os.path.exists(self.file_path):
            os.system("mkdir -p %s"%(self.file_path))
        file_path = os.path.join(self.file_path,self.file_name)
        self.marmo_log["datas"].append("file path==" + str(file_path))
        command = self.command%(self.port,self.ip,file_path)
        self.marmo_log["datas"].append("port banner command ==" + str(command))
        logger.log(command)
        runcode = os.system(command)
        if runcode ==0 or runcode =="0":
            '''
                读取端口xml文件
            '''
            self.read_xml_file(file_path)
            '''
                更新端口的version 和banner
            '''
        else:
            raise Exception("执行nmap命令出现异常==="+str(runcode))
        # except Exception as e:
        #     logger.log("执行端口扫描出现异常== "+str(e.__str__()))
        #     raise Exception("执行端口扫描出现异常== "+str(e.__str__()))




    '''
        读取xml文件
    '''
    def read_xml_file(self,file_path):
        # try:
            domTree = parse(file_path)
            rootNode=domTree.documentElement
            ports = rootNode.getElementsByTagName("port")
            for port in ports:
                protocol=""
                portid=""
                state=""
                name=""
                version=""
                tunnel=""
                if port.hasAttribute("protocol"):
                    protocol=port.getAttribute("protocol")
                if port.hasAttribute("portid"):
                    portid=port.getAttribute("portid")
                state_elements = port.getElementsByTagName("state")
                if len(state_elements) >=1:
                    state_element = state_elements[0]
                    if state_element.hasAttribute("state"):
                        state = state_element.getAttribute("state")
                services = port.getElementsByTagName("service")
                if len(services) >=1:
                    service =services[0]
                    if service.hasAttribute("name"):
                        name = service.getAttribute("name")
                    if service.hasAttribute("tunnel"):
                        tunnel = service.getAttribute("tunnel")
                    if service.hasAttribute("version"):
                        version = service.getAttribute("version")
                source_detail ="protocol=%s ,portid=%s ,state=%s ,name=%s, version=%s "%(str(protocol),str(portid),str(state),str(name),str(version))
                logger.log(source_detail)
                self.marmo_log["datas"].append("source detail==" + str(source_detail))
                self.version =version
                self.banner =name
                '''
                    banner探测之后更新端口的service和version
                '''
                update_params ={
                    "project_name":self.asset_data["project_name"],
                    "asset_id":self.asset_data["asset_id"],
                    "asset":self.ip
                }
                logger.log("name ==="+str(name))
                self.marmo_log["datas"].append("name==" + str(name))
                if name:
                    self.exists_data =True
                    update_params["banner"] = name
                    '''
                        判断类型
                    '''
                    if "https" in name or "ssl" in name:
                        update_params["srv_type"]=2
                    elif "http" in name and "https" not in name:
                        update_params["srv_type"]=1
                    else:
                        if portid:
                            if "80" ==str(portid):
                                update_params["srv_type"] = 1
                            elif "443" ==str(portid):
                                update_params["srv_type"] = 2
                            elif str(portid).startswith("80"):
                                update_params["srv_type"] = 1
                            else:
                                update_params["srv_type"] =9

                if tunnel:
                    if "ssl" in tunnel or "ISS" in tunnel:
                        update_params["srv_type"]=2

                if source_detail:
                    update_params["source_detail"]=source_detail
                if version:
                    update_params["version"]=version
                logger.log("update_params ==="+str(update_params))
                self.marmo_log["datas"].append("update params==" + str(update_params))
                ServiceDao().update_service(update_params)
                break
        # except Exception as e:
        #     logger.log("读取xml文件出现异常=="+str(e.__str__()))
        #     raise Exception("读取xml文件出现异常=="+str(e.__str__()))


    '''
        run函数
    '''
    def run(self):
        try:
            self.run_command()
            self.data_info["status_code"]=2
            self.data_info["exists_data"]=self.exists_data
        except Exception as e:
            self.data_info["exists_data"]=False
            self.data_info["status_code"]=3
            self.data_info["fail_reason"]="端口banner探测出现异常="+str(e.__str__())
            self.marmo_log["exceptions"].append("端口banner探测出现异常="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "PORT_BANNER",
                "type": '3',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info


if __name__ =="__main__":
    portbanner=PortBanner({"port":9079,"ip":"139.155.75.152"})
    portbanner.run_command()





