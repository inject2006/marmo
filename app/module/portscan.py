# -*- coding:UTF-8 -*-
'''
    端口扫描模块
    注意:不能使用后台任务执行,如果执行端口扫描那项目基本上不能发网络请求
'''
from app.dao.marmo_log_dao import MarmoLogDao
from app.dao.service_dao import ServiceDao
import os
import re
import json
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()
from marmo.settings import MASSCAN_FILE_PATH,MASSCAN_COMMAND,RUSTSCAN_ALL_PORT_COMMAND,RUSTSCAN_PART_PORT_COMMAND,PORT_TOP
from marmo.settings import SERVICE_CELERY_STATUS
class PortScan():
    def __init__(self,asset_data):
        self.asset_data =asset_data
        self.all_port_command =RUSTSCAN_ALL_PORT_COMMAND
        self.part_port_command =RUSTSCAN_PART_PORT_COMMAND
        self.ip =asset_data["asset"]
        self.rustscan_ip_set=set()
        self.massscan_ip_set =set()
        self.masscan_command= MASSCAN_COMMAND
        self.file_path =MASSCAN_FILE_PATH
        self.file_name = str(self.ip)+".json"
        self.port_top=PORT_TOP #端口大于这个数就认为是异常
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



    '''
        ip端口全扫描
        进行端口探测的端口不知道是否是web还是not_web
    '''
    def ScanAllPort(self):
        # try:
        command = self.all_port_command%(self.ip)
        logger.log("rustscan command =="+str(command))
        self.marmo_log["datas"].append("rustscan all port command =="+str(command))
        ipresults = os.popen(command)
        ip_result =""
        for ip in ipresults:
            ip_result+=ip
        self.marmo_log["datas"].append("rustscan扫描结果=="+str(ip_result))
        if "->" in ip_result:
            ip_split_results = ip.split("-> ")
            ports = ip_split_results[1]
            logger.log(ports)
            if "[" in ports and "]" in ports:
                ports_list = eval(ports)
                self.marmo_log["datas"].append(" port list =="+str(ports_list))
                if len(ports_list) >=self.port_top: #端口数量是否大于指定数量50个，ip进入待定列表
                        self.marmo_log["datas"].append("rustscan 端口数大于50 ")
                        self.run_masscan()
                        self.marmo_log["datas"].append("massscan扫描结果="+str(self.massscan_ip_set))
                        if len(self.massscan_ip_set) >=self.port_top:
                            self.data_info["exists_data"]=False
                            self.data_info["status_code"]=3
                            self.data_info["fail_reason"]="rustscan端口数和massscan端口数都大于等于50，ip是%s"%str(self.ip)
                            raise Exception("rustcan 和masscan对ip%s进行端口扫描数量都大于50，异常ip")
                        else:
                            '''
                                massscan端口的数量小于50，端口入库，rustscan数据不入库
                            '''
                            service_dao =ServiceDao()
                            if len(self.massscan_ip_set) >=1:
                                self.data_info["exists_data"]=True
                                self.data_info["status_code"]=2
                                self.data_info["data"]=str(self.massscan_ip_set)
                            else:
                                self.data_info["status_code"] = 2
                            while len(self.massscan_ip_set) >=1:

                                port = self.massscan_ip_set.pop()
                                '''
                                    端口探测的类型为未知 srv_type
                                '''
                                add_port_params ={
                                    "port":int(port),
                                    "description":"masscan 扫描进行添加",
                                    "asset":self.ip,
                                    "source":1,
                                    "project_name":self.asset_data["project_name"],
                                    "is_deep_http_recongnize":2,
                                    "srv_type":0,
                                    "source_detail": "masscan 扫描进行添加",
                                    "web_type":"unknow",
                                    "celery_status":SERVICE_CELERY_STATUS,
                                    "asset_type":2
                                }
                                service_dao.create_service(add_port_params)
                else:
                    '''
                        rustscan扫出的端口数量小于50，端口入库
                    '''
                    for port in ports_list:
                        self.rustscan_ip_set.add(port)
                    logger.log(self.rustscan_ip_set)
                    if len(self.rustscan_ip_set) >= 1:
                        self.data_info["exists_data"] = True
                        self.data_info["status_code"] = 2
                        self.data_info["data"] = str(self.rustscan_ip_set)
                    else:
                        self.data_info["status_code"] = 2
                    service_dao = ServiceDao()
                    while len(self.rustscan_ip_set) >=1:
                        port = self.rustscan_ip_set.pop()
                        add_port_params = {
                            "port": int(port),
                            "description": "rustscan 扫描进行添加",
                            "asset": self.ip,
                            "source": 1,
                            "project_name": self.asset_data["project_name"],
                            "is_deep_http_recongnize": 2,
                            "srv_type":0,
                            "source_detail":"rustscan 扫描进行添加",
                            "web_type": "unknow",
                            "celery_status":SERVICE_CELERY_STATUS,
                            "asset_type": 2
                        }
                        service_dao.create_service(add_port_params)

        # except Exception as e:
        #     logger.log("端口扫描出现异常=="+str(e.__str__()))


    '''
        扫描部分端口函数
    '''
    def scan_part_port(self):
        # try:
            command = self.part_port_command % (self.ip)
            logger.log("rustscan part port command ==" + str(command))
            ipresults = os.popen(command)
            ip_result =""
            for ip in ipresults:
                ip_result+=ip
            if "->" in ip_result:
                ip_split_results = ip.split("-> ")
                ports = ip_split_results[1]
                logger.log(ports)
                if "[" in ports and "]" in ports:
                    ports_list = eval(ports)
                    if len(ports_list) >= self.port_top:
                        self.run_masscan()
                        self.marmo_log["datas"].append("massscan扫描结果=" + str(self.massscan_ip_set))
                        if len(self.massscan_ip_set) >= self.port_top:
                            self.data_info["exists_data"] = False
                            self.data_info["status_code"] = 3
                            self.data_info["fail_reason"] = "rustscan端口数和massscan端口数都大于等于50，ip是%s" % str(self.ip)
                            raise Exception("rustcan 和masscan对ip%s进行端口扫描数量都大于50，异常ip")
                        else:
                            '''
                                massscan端口的数量小于50，端口入库，rustscan数据不入库
                            '''
                            service_dao = ServiceDao()
                            if len(self.massscan_ip_set) >= 1:
                                self.data_info["exists_data"] = True
                                self.data_info["status_code"] = 2
                                self.data_info["data"] = str(self.massscan_ip_set)
                            else:
                                self.data_info["status_code"] = 2
                            while len(self.massscan_ip_set) >= 1:
                                port = self.massscan_ip_set.pop()
                                '''
                                    端口探测的类型为未知 srv_type
                                '''
                                add_port_params = {
                                    "port": int(port),
                                    "description": "masscan 扫描进行添加",
                                    "asset": self.ip,
                                    "source": 1,
                                    "project_name": self.asset_data["project_name"],
                                    "is_deep_http_recongnize": 2,
                                    "srv_type": 0,
                                    "source_detail": "masscan 扫描进行添加",
                                    "web_type": "unknow",
                                    "celery_status":SERVICE_CELERY_STATUS,
                                    "asset_type": 2
                                }
                                service_dao.create_service(add_port_params)

                    else:
                        '''
                            rustscan扫出的端口数量小于50，端口入库
                        '''
                        for port in ports_list:
                            self.rustscan_ip_set.add(port)
                        logger.log(self.rustscan_ip_set)
                        if len(self.rustscan_ip_set) >= 1:
                            self.data_info["exists_data"] = True
                            self.data_info["status_code"] = 2
                            self.data_info["data"] = str(self.rustscan_ip_set)
                        else:
                            self.data_info["status_code"] = 2
                        service_dao = ServiceDao()
                        while len(self.rustscan_ip_set) >=1:
                            port = self.rustscan_ip_set.pop()
                            add_port_params = {
                                "port": int(port),
                                "description": "rustscan 扫描C段IP%s进行添加"%(self.ip),
                                "asset": self.ip,
                                "source": 1,
                                "project_name": self.asset_data["project_name"],
                                "is_deep_http_recongnize": 2,
                                "srv_type":0,
                                "source_detail":"rustscan 扫描C段IP%s进行添加"%(self.ip),
                                "web_type": "unknow",
                                "celery_status":SERVICE_CELERY_STATUS,
                                "asset_type": 2
                            }
                            service_dao.create_service(add_port_params)

        # except Exception as e:
        #     logger.log("端口扫描出现异常==" + str(e.__str__()))


    '''
        执行masscan命令进行扫描
    '''
    def run_masscan(self):
        try:
            '''
                需要用到masscan
            '''
            if not os.path.exists(self.file_path):
                os.system("mkdir -p %s" % (self.file_path))
            mass_file_name = os.path.join(self.file_path, self.file_name)
            self.marmo_log["datas"].append("masscan file name == "+str(mass_file_name))
            masscan_command = self.masscan_command % (self.ip, mass_file_name)
            logger.log("masscan 命令==="+str(masscan_command))
            self.marmo_log["datas"].append("masscan 命令==="+str(masscan_command))
            runcode = os.system(masscan_command)
            if runcode == 0 or runcode == "0":
                '''
                    masscan执行成功,读取生成文件

                '''
                self.read_mass_file(mass_file_name)
            else:
                raise Exception("执行masscan命令出错")
        except Exception as e:
            logger.log("执行run_masscan命令出现异常=="+str(e.__str__()))




    '''
        读取mass文件
        [
{   "ip": "42.194.177.125",   "timestamp": "1620636178", "ports": [ {"port": 6379, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 53} ] }
,
{   "ip": "42.194.177.125",   "timestamp": "1620636231", "ports": [ {"port": 7890, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 53} ] }
,
{   "ip": "42.194.177.125",   "timestamp": "1620636239", "ports": [ {"port": 60000, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 53} ] }
,
{   "ip": "42.194.177.125",   "timestamp": "1620636242", "ports": [ {"port": 23456, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 53} ] }
,
{   "ip": "42.194.177.125",   "timestamp": "1620636281", "ports": [ {"port": 22, "proto": "tcp", "status": "open", "reason": "syn-ack", "ttl": 53} ] }
]
    '''
    def read_mass_file(self,filename):
        with open(filename, "r", encoding="UTF-8") as f:
            results = f.read()
            self.marmo_log["datas"].append("read mass file result =="+str(results))
            # pattern = '["]*port["]*:(.*?),'
            if results:
                results = json.loads(results)
            for result in results:
                if result.__contains__("ports"):
                    ports = result["ports"]
                    for port in ports:
                        detail_port = port["port"]
                        self.massscan_ip_set.add(detail_port)
            # res = re.findall(pattern, results, re.S)
            # logger.log(res)
            # for port in res:
            #     if port:
            #         other_port = "".join(port.split())
            #         self.massscan_ip_set.add(other_port)



    '''
        根据type区分是全部端口扫描还是部分端口扫描
    '''
    def run(self):
        try:
            logger.log("portscan run")
            self.marmo_log["datas"].append("port scan run ")
            if self.asset_data["type"]==1:
                self.marmo_log["datas"].append(" scan all port  ")
                self.ScanAllPort()
            elif self.asset_data["type"] ==4:
                self.marmo_log["datas"].append(" scan part port  ")
                self.scan_part_port()
        except Exception as e:
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
            self.data_info["fail_reason"]="端口扫描出现异常="+str(e.__str__())
            self.marmo_log["exceptions"].append("端口扫描出现异常=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "PORTSCAN",
                "type": '3',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info


if __name__ =="__main__":
    portscan = PortScan({"ip":"139.155.75.152"})
    portscan.run()


