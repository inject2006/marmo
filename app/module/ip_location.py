# -*- coding:UTF-8 -*-
'''
    ip位置和出口诊断模块
'''
import requests
import re
import json
from app.dao.online_asset_ip_dao import OnlineAssetIpDao
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()
class IPLocation():
    def __init__(self,asset_data):
        self.ip_location_url="https://www.ip138.com/iplookup.asp?ip=%s&action=2"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Host": "site.ip138.com"
        }
        self.ip =asset_data["asset"]
        self.asset_data =asset_data
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
            解析ip地址位置和出口
        '''

    def get_ip_location(self):
        # try:
            headers = self.headers
            headers["Host"] = "www.ip138.com"
            ip_url = self.ip_location_url % (self.ip)
            self.marmo_log["datas"].append("ip location url =="+str(ip_url))
            res = requests.get(ip_url, headers=headers)

            if res.status_code == 200:
                '''
                    这里有个担心，如果用requests返回的encoding会乱码，直接写死gb23112有可能在后续也会乱码
                '''
                text = res.content.decode(encoding="gb2312")
                # self.marmo_log["datas"].append("ip location text =="+str(text))
                pattern = "var ip_result = (.*?);"
                ip_results = re.findall(pattern, text, re.S)
                if ip_results and len(ip_results) >= 1:
                    ip_result = ip_results[0]
                    ip_json = json.loads(ip_result)
                    ip_c_list = ip_json["ip_c_list"]
                    location_string = ""
                    for ip_obj in ip_c_list:  # 通常情况下只有一个
                        ct = ip_obj["ct"]
                        prov = ip_obj["prov"]
                        city = ip_obj["city"]
                        yunyin = ip_obj["yunyin"]
                        location_string += "国家:" + ct + " 省份:" + prov + " 城市:" + city + " 运营商:" + yunyin
                    if location_string:
                        self.data_info["exists_data"]=True
                        self.data_info["data"]=location_string
                        self.data_info["status_code"]=2
                    else:
                        self.data_info["exists_data"] = False
                        self.data_info["status_code"] = 2
                    self.marmo_log["datas"].append(location_string)
                    logger.log("ip地理位置模块输出地址=="+str(location_string))
                    update_params ={
                        "ip":self.asset_data["asset"],
                        "project_name":self.asset_data["project_name"],
                        "project_id":self.asset_data["project_id"],
                        "asset_id":self.asset_data["asset_id"],
                        "location":location_string

                    }
                    update_location = OnlineAssetIpDao().upate_location(update_params)
            else:
                raise Exception("获取ip地址和出口状态码异常==" + str(res.status_code))
        # except Exception as e:
        #     print("获取ip地址和出口异常==" + str(e.__str__()))
        #     return False

    '''
        run函数
    '''
    def run(self):
        try:
            self.get_ip_location()
        except Exception as e:
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
            self.data_info["fail_reason"]="获取ip地理位置出现异常="+str(e.__str__())
            self.marmo_log["exceptions"].append("获取ip地理位置出现异常="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "IP_LOCATION",
                "type": '2',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info


if __name__ =="__main__":
    iplocation=IPLocation({"ip":"139.155.75.152"})
    iplocation.run()
