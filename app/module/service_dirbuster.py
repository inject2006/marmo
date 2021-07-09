# -*- coding:UTF-8 -*-
'''
    目录爆破
    条件:web资产
'''
import os
import re
import json
from app.dao.online_asset_ip_dao import OnlineAssetIpDao
from app.dao.asset_dao import AssetDao
from marmo.settings import DIRBUSTER_DISTIONARY,DIRBUSTER_DEEP,DIRBUSTER_OUTPUT,DIRBUSTER_COMMAND
from app.dao.marmo_log_dao import MarmoLogDao
from urllib import parse
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()
class DirBuster():
    def __init__(self,asset_data):
        self.dirbuster_dictionary=DIRBUSTER_DISTIONARY #字典
        self.deep =DIRBUSTER_DEEP #递归深度
        self.proxy =""  #代理 -p socks5://192.168.0.144:7890
        self.output=DIRBUSTER_OUTPUT  #输出目录
        self.url =""  #拼接好的目录
        self.port =asset_data["port"]  #端口
        self.ip=asset_data["asset"]
        self.domain=asset_data["domain"]
        self.protocol_type=asset_data["srv_type"]  #http 或者https
        self.command=DIRBUSTER_COMMAND
        self.dir_results =""
        self.asset_data= asset_data
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
        运行命令
        文件名:可以是ip开头或者域名开头
    '''
    def run_command(self,url,filename,asset_type):
        if not os.path.exists(self.output):
            os.system("mkdir -p %s"%(self.output))
        file_name = os.path.join(self.output,str(filename)+".txt")
        self.marmo_log["datas"].append("run_command file name=="+str(file_name))
        command = self.command%(self.dirbuster_dictionary,file_name,url)
        logger.log(command)
        self.marmo_log["datas"].append("目录爆破命令="+str(command))
        run_code = os.system(command)
        if run_code ==0 or run_code =="0":
            '''
                读取文件
            '''
            with open(file_name,"r",encoding="UTF-8") as f:
                lines = f.readlines()
                dirs = []
                for line in lines:
                    if "dirsearch.py" not in line:
                        line_line = line.split("   ")
                        if len(line_line) ==3:
                            dir_obj = {}
                            url =line_line[2]
                            if url:
                                url = parse.quote(url)
                            dir_obj["url"] = url
                            dir_obj["status"] =line_line[0]
                            dir_obj["content_length"] = line_line[1]
                            dirs.append(dir_obj)
                        elif len(line_line) >=4:
                            dir_obj = {}
                            url = line_line[2]+line_line[3]
                            if url:
                                url = parse.quote(url)
                            dir_obj["url"] = url
                            dir_obj["status"] = line_line[0]
                            dir_obj["content_length"] = line_line[1]
                            dirs.append(dir_obj)
                self.marmo_log["datas"].append("dirs =="+str(dirs))
                if dirs and len(dirs) >=1:
                    self.data_info["exists_data"]=True
                    self.data_info["status_code"]=2
                    self.data_info["data"]=str(dirs)
                else:
                    self.data_info["status_code"] = 2
                    self.data_info["exists_data"]=False

                '''
                    插入到资产表的dirbuster字段中
                '''
                if asset_type ==2:
                    update_params ={
                        "project_name":self.asset_data["project_name"],
                        "asset_id":self.asset_data["asset_id"],
                        "ip":self.ip,
                        "dirbuster":dirs
                    }
                    self.marmo_log["datas"].append("dirbuster update params ==" + str(update_params))
                    ip_dao =OnlineAssetIpDao()
                    ip_dao.update_dirbuster(update_params)
                elif asset_type ==1:
                    '''
                        更新域名表的目录爆破字段
                    '''
                    update_params = {
                        "project_name": self.asset_data["project_name"],
                        "asset_id": self.asset_data["asset_id"],
                        "domain": self.domain,
                        "dirbuster": dirs
                    }
                    self.marmo_log["datas"].append("dirbuster update params ==" + str(update_params))
                    AssetDao().update_domain_dirbuster(update_params)
    '''
        运行
        查询web端口-查询端口关联的ip-查询ip关联的父资产(域名/ip),如果是域名,那么要进行两个目录爆破,如果是ip,只进行本身的ip目录爆破
    '''
    def run(self):
        try:
            if self.ip and not self.domain: #ip进行目录爆破
                url=str(self.protocol_type)+"://"+str(self.ip)+":"+str(self.port)
                self.marmo_log["datas"].append("run url ==" + str(url))
                filename =str(self.ip) +"_"+str(self.port)+"_2"
                self.marmo_log["datas"].append("run filename ="+str(filename))
                self.run_command(url, filename, 2)
            elif self.domain and not self.ip: #域名进行爆破
                url = str(self.protocol_type) + "://" + str(self.domain) + ":" + str(self.port)
                self.marmo_log["datas"].append("run url ==" + str(url))
                filename =str(self.domain) +"_"+str(self.port)+"_1"
                self.marmo_log["datas"].append("run filename =" + str(filename))
                self.run_command(url, filename, 1)
            elif self.domain and self.ip:
                domain_url = str(self.protocol_type)+"://"+str(self.domain)+":"+str(self.port)
                self.marmo_log["datas"].append("run url ==" + str(domain_url))
                filename = str(self.domain)+"_"+str(self.ip)+str(self.port)+"_1"
                self.marmo_log["datas"].append("run filename =" + str(filename))
                self.run_command(domain_url,filename,1)
                ip_url = str(self.protocol_type) + "://" +str(self.ip)+ ":"+ str(self.port)
                self.marmo_log["datas"].append("run url ==" + str(ip_url))
                filename = str(self.domain)+"_"+str(self.ip)+str(self.port)+"_2"
                self.marmo_log["datas"].append("run filename =" + str(filename))
                self.run_command(ip_url, filename, 2)
        except Exception as e:
            logger.log("进行目录爆破时出现异常=="+str(e.__str__()))
            self.data_info["exists_data"]=False
            self.data_info["status_code"]=3
            self.data_info["fail_reason"]="进行目录爆破时出现异常=="+str(e.__str__())
            self.marmo_log["exceptions"].append("进行目录爆破时出现异常=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "DIRBUSTER",
                "type": '3',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info



if __name__ =="__main__":
    dirbuster =DirBuster({"domain":"www.kerororo.com","port":"443","protocol_type":"https","ip":""})
    dirbuster.run()




