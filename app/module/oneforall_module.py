# -*- coding:UTF-8 -*-
'''
    功能:
    子域名收集:python3 oneforall.py --fmt json --path xxx --target baidu.com run --brute=False
    子域名爆破:gobuster dns -t 50 -d baidu.com -w worldlist.txt -o result.txt
    input:
    {
        domain_name
        project_id
        asset_id
        asset_type
        project_name
        module_name
    }
    注意：oneforall的结果和gobuster的结果要去重
'''
import os
import json
from marmo.settings import ONEFORALLPATH,ONEFORALL_COMMAND
from app.dao.asset_dao import AssetDao
from app.exceptions.module_exception import ModuleException
from .goBuster_module import GoBuster
from django_redis import get_redis_connection
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
from marmo.settings import SUBDOMAIN_CELERY_STATUS
logger = Marmo_Logger()
class OneForAll():
    def __init__(self,asset_data):
        assert ONEFORALLPATH
        self.asset_data = asset_data
        self.target =asset_data["domain_name"]
        self.oneforall_path=ONEFORALLPATH
        self.module_name=asset_data["module_name"]
        self.domain_set = set()
        self.module_log=""
        self.project_name = asset_data["project_name"]
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

    def run_oneforall(self):
            assert self.target
            # cmd_command = "/usr/local/bin/python3 " + str(self.oneforall_path) + "/oneforall.py --fmt json --path "+os.path.join(self.oneforall_path,self.target+".json")+" --target " + str(
            #     self.target) + " run --brute=False"
            cmd_command =ONEFORALL_COMMAND%(str(self.oneforall_path) + "/oneforall.py",os.path.join(self.oneforall_path,self.target+".json"),str(self.target))
            logger.log(cmd_command)
            self.marmo_log["datas"].append("执行oneforall命令= "+str(cmd_command))
            run_code = os.system(cmd_command)
            if run_code =="0" or run_code==0:
                return True
            else:
                self.marmo_log["exceptions"].append("执行oneforall出现异常=="+str(run_code))
                raise Exception("执行oneforall出现异常=="+str(run_code))

    def read_oneforall_result(self):
        # try:
            '''
                读取oneforall命令
                [{"id": 11, "alive": 0, "request": 0, "resolve": 1, "url": "https://bpm.wkjyqh.com", "subdomain": "bpm.wkjyqh.com", "level": 1, "cname": "bpm.wkjyqh.com", "ip": "120.86.113.171", "public": 1, "cdn": 0, "port": 443, "status": null, "reason": "('check_hostname requires server_hostname',)", "title": null, "banner": null, "cidr": "120.86.64.0/18", "asn": "AS17816", "org": "China Unicom", "addr": "\u4e2d\u56fd\u5e7f\u4e1c\u7701\u4e1c\u839e\u5e02", "isp": "\u8054\u901a", "source": "Brute"}]
            '''
            file_path = os.path.join(self.oneforall_path,self.target+".json")
            self.marmo_log["datas"].append("读取oneforall 文件路径=="+str(file_path))
            with open(file_path,"r",encoding="UTF-8") as f:
                result = f.read()
                # if not isinstance(result,str):
                result = json.loads(result)
                self.module_log+=str(result)
                if result and len(result) >=1:
                    for one in result:
                        '''
                            获取二级域名
                        '''
                        if one and one.__contains__("subdomain"):
                            subdomain = one["subdomain"]
                            if subdomain:
                                self.domain_set.add(subdomain.lower())
                self.marmo_log["datas"].append("读取oneforall获取到的子域名="+str(self.domain_set))




    '''
        运行模块
    '''
    def run(self):
        try:
            '''
                先暂时注销掉一主域名爆破
            '''
            run_oneforall_result=self.run_oneforall()
            if run_oneforall_result:
                    self.read_oneforall_result() #oneforall的结果
                    gobuster = GoBuster(self.asset_data) #gobuster的结果
                    go_buster_result=gobuster.run()
                    # go_buster_result =set(["www.nucc.com","mail.nucc.com","download.nucc.com","im.nucc.com","mx01.nucc.com","MAIL.nucc.com","WWW.nucc.com"])
                    self.domain_set.update(go_buster_result) #oneforall和goBuster结果去重
                    assetdao = AssetDao()
                    if len(self.domain_set) >=1:
                        self.data_info["exists_data"]=True
                        self.data_info["status_code"]=2
                        self.data_info["data"]=str(self.domain_set)
                    else:
                        self.data_info["status_code"]=2
                        self.data_info["exists_data"] = False
                    while True:
                        if len(self.domain_set) >=1:
                            subdomain = self.domain_set.pop()
                            add_domain_params={
                                "domain_name": subdomain,
                                "source": 1,
                                "project_id": self.asset_data["project_id"],
                                "description": str(self.module_name)+"进行子域名收集&爆破模块获取到的域名",
                                "source_detail": "",
                                "domain_type": 2,
                                "is_include_cdn_ip": 2,
                                "project_name":self.asset_data["project_name"],
                                "celery_status":SUBDOMAIN_CELERY_STATUS
                            }
                            assetdao.create_domain(add_domain_params)
                            self.marmo_log["datas"].append("ip数据入库完成="+str(add_domain_params))
                        else:
                            '''
                                全部子域名入库完毕
                            '''
                            redis_connection = get_redis_connection("default")
                            redis_connection.hset(self.project_name,"main_domain",2)
                            break

            else:
                raise Exception("执行oneforall出现异常")
        except ModuleException as me:
            print("执行oneforall出现异常==="+str(me.__str__()))
            self.data_info["fail_reason"]="执行oneforall出现异常==="+str(me.__str__())
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
        except Exception as e:
            print("执行oneforall出现异常=="+str(e.__str__()))
            self.data_info["fail_reason"]="执行oneforall出现异常=="+str(e.__str__())
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "ONEFORALL",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info

if __name__ =="__main__":
    oneforall = OneForAll("keroro.com","/data/OneForAll")
    oneforall.run()