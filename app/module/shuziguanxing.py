#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name shuziguanxing
__time__ = "2021/6/9 11:02"
import requests
import json
from app.utils.marmo_logger import Marmo_Logger
from app.dao.marmo_log_dao import MarmoLogDao
logger = Marmo_Logger()
class ShuZiGuanXing():
    def  __init__(self,domain,srv_type,asset_id):
        self.url ="https://fp.shuziguanxing.com/fp/fingerprintWarehouse/resultList"
        self.search_url ="https://fp.shuziguanxing.com/fp/fingerprintWarehouse/search"
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "X-KL-Ajax-Request": "Ajax_Request",
            "Referer": "https://fp.shuziguanxing.com/",
            "Host":"fp.shuziguanxing.com",
            "Origin":"https://fp.shuziguanxing.com",
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "sec-ch-ua-mobile": "?0",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Accept":"application/json,text/plain,*/*",
            "Accept-Language":"zh-CN,zh;q=0.9",
            "Content-Type":"application/json;charset=UTF-8"
        }
        self.domain =domain
        self.srv_type = srv_type
        self.asset_id = asset_id
        self.componet_list =[]
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }

    def search(self):
        url = str(self.srv_type) + "://" + str(self.domain)
        logger.log("shuziguanxing url =="+str(url))
        self.marmo_log["datas"].append("shuziguanxing url =="+str(url))
        post_data = {
            "appUrl": {"url":url}
        }
        res = requests.post(self.search_url, headers=self.headers, data=json.dumps(post_data))
        if res.status_code == 200:
            result_text = res.text
            print(result_text)
            self.marmo_log["datas"].append("search data=="+str(result_text))
            if result_text:
                result_json=json.loads(result_text)
                if result_json.__contains__("state") :
                    state = result_json["state"]
                    if state ==1 or state =="success":
                        return self.get_data()


    def get_data(self):
        try:
            url =self.srv_type+"://"+self.domain
            logger.log("shuziguanxing get data url ==" + str(url))
            self.marmo_log["datas"].append("shuziguanxing url ==" + str(url))
            post_data={
                "appUrl":{"url":url}
            }
            res =requests.post(self.url,headers=self.headers,data=json.dumps(post_data))
            if res.status_code ==200:
                result_text = res.text
                print(result_text)
                self.marmo_log["datas"].append("shuziguanxing get data result ==" + str(result_text))
                if result_text:
                    result_json = json.loads(result_text)
                    if result_json.__contains__("state"):
                        state = result_json["state"]
                        if state =="success" or state ==1:
                            info=result_json["info"]
                            if info:
                                if info.__contains__("state") and info["state"]==1:
                                    appInfos = info["appInfos"]
                                    for app in appInfos:
                                        obj ={}
                                        if app.__contains__("name"):
                                            component_name = app["name"]
                                            if component_name:
                                                obj["name"]=component_name.lower()
                                                obj["version"]=""
                                                obj["source_detail"]="从数字观星网站对域名%s进行cms识别获取到的组件 %s"%(url,component_name)
                                                self.componet_list.append(obj)
                                # return self.componet_list
        except Exception as e:
            self.marmo_log["exceptions"].append("数字观星获取数据出现异常=="+str(e.__str__()))
            print("数字观星获取数据出现异常=="+str(e.__str__()))
            raise Exception("数字观星获取数据出现异常=="+str(e.__str__()))


    def run(self):
        try:
            self.get_data()
        except Exception as e:
            self.marmo_log["exceptions"].append("数字观星 run 出现异常==" + str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "SHUZIGUANXING",
                "type": '4',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_id)
            }
            MarmoLogDao().add_log(add_log_params)
            return self.componet_list

if __name__ =="__main__":
    shuziguanxing = ShuZiGuanXing(srv_type="https",domain="139.155.75.152:443")
    shuziguanxing.run()



