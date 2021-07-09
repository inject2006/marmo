# -*- coding:UTF-8 -*-
'''
    获取ip的c段地址
'''
from app.dao.asset_dao import AssetDao
import re
import os
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
from marmo.settings import IP_CELERY_STATUS
logger = Marmo_Logger()
class CDuan():
    def __init__(self,asset_data):
        # super(Base).__init__()
        self.crange_set =set()
        self.asset_data =asset_data
        self.module_name=asset_data["module_name"]
        self.command="nmap -sP %s -oG - |awk '{print $2}'|awk 'NR>2{print line}{line=$0}'"
        self.ip =asset_data["asset"]
        self.sub_ip_set= set()
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
        生成c段
        input:ip地址
        output:ip地址的C段
    '''
    def make_crange(self):
        try:
            assert self.ip
            rez = re.compile(r'\d+\.\d+\.\d+\.')
            ip_c_range = rez.findall(self.ip)
            if ip_c_range and len(ip_c_range)>=1:
                for ip_range in ip_c_range:
                    self.crange_set.add(str(ip_range)+"0/24")
        except Exception as e:
            self.marmo_log["exceptions"].append("make crange 出现异常=="+str(e.__str__()))
            raise Exception("make crange 出现异常=="+str(e.__str__()))


    '''
        执行nmap命令
    '''
    def run_command(self):
        try:
            while len(self.crange_set) >=1:
                crange_ip = self.crange_set.pop()
                command = self.command%(crange_ip)
                self.marmo_log["datas"].append("执行command="+str(command))
                logger.log("crange command ==="+str(command))
                results =os.popen(command)
                for result in results:

                    self.sub_ip_set.add(result)
                '''
                    判断是否有数据,是否执行成功
                '''
                self.marmo_log["datas"].append("执行crange command 结果==" + str(self.sub_ip_set))
                logger.log("crange results ==="+str(self.sub_ip_set))
                '''
                    把c段ip插入数据表中
                '''
                assetdao =AssetDao()
                while len(self.sub_ip_set) >=1:
                    ip = self.sub_ip_set.pop()
                    '''
                        c段衍生出的ip状态直接改成待出口诊断
                    '''
                    add_ip_params={
                        "ip_type":4,
                        "ip":ip,
                        "source":1,
                        "description":"通过c段扫描模块对%s进行扫描添加"%(self.ip),
                        "is_belongs_to":1,
                        "project_name":self.asset_data["project_name"],
                        "related_ip":self.ip,
                        "celery_status":IP_CELERY_STATUS
                    }
                    self.marmo_log["datas"].append("crange add ip params=="+str(add_ip_params))
                    assetdao.create_ip(add_ip_params)
                    logger.log("插入ip数据成功")
                    self.marmo_log["datas"].append("插入ip数据成功="+str(add_ip_params))
        except Exception as e:
            logger.log("c段模块更新模块功能出现异常=="+str(e.__str__()))
            self.marmo_log["exceptions"].append("c段模块更新模块功能出现异常=="+str(e.__str__()))

    '''3
        run函数
    '''
    def run(self):
        try:
            self.make_crange()
            logger.log("crange set =="+str(self.crange_set))
            self.marmo_log["datas"].append("crange set =="+str(self.crange_set))
            self.run_command()
            if len(self.sub_ip_set) >=1:
                self.data_info["exists_data"]=True
                self.data_info["status_code"]=2
                self.data_info["data"]=str(self.sub_ip_set)
            else:
                self.data_info["status_code"] = 2
        except Exception as e:
            self.data_info["status_code"]=3
            self.data_info["fail_reason"]="获取C段IP出现异常"+str(e.__str__())
            print("获取C段IP出现异常"+str(e.__str__()))
            self.marmo_log["exceptions"].append("获取C段IP出现异常"+str(e.__str__()))
        finally:
            '''
                marmo_log数据入库
            '''
            add_log_params = {
                "module": "CRANGE",
                "type": '2',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info


if __name__ =="__main__":
    cduan = CDuan({})
    c=cduan.make_crange("42.194.177.125")
    print(c)

