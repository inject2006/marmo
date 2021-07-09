#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name marmo_whatruns
__time__ = "2021/6/9 18:28"
'''
    cms识别
'''
import requests
import json
from urllib.parse import quote,urlencode
from app.dao.marmo_log_dao import MarmoLogDao
class WhatRuns():
    def __init__(self,domain,srv_type,asset_id):
        self.url ="https://www.whatruns.com/api/v1/get_site_apps"
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Content-Type":"application/x-www-form-urlencoded",
            "Host":"www.whatruns.com"
        }
        self.domain =domain
        self.srv_type =srv_type
        self.asset_id = asset_id
        self.web_recongnize_set =[]
        self.marmo_log ={
            "datas":[],
            "exceptions":[]
        }

    def get_data(self):
        try:
            if "." in self.domain:
                domain_list = self.domain.split(".")
                if len(domain_list) ==3:
                    subdomain=domain_list[0]
                    url =self.srv_type+"://"+self.domain
                    url=url.replace("/","%2F")
                    self.marmo_log["datas"].append("what runs url =="+str(url))
                    post_data='{"rawhostname":"%s","hostname":"%s","subdomain":"%s","url":"%s","type":"ajax"}'%(self.domain,self.domain,subdomain,url)
                    self.marmo_log["datas"].append("post data =="+str(post_data))
                    res = requests.post(self.url,data="data="+quote(post_data,safe="/"),headers=self.headers)
                    if res.status_code ==200:
                        print(res.text)
                        result_json = res.json()
                        self.marmo_log["datas"].append("whatruns json =="+str(result_json))
                        if result_json.__contains__("apps"):
                            apps = result_json["apps"]
                            if apps:
                                apps_json = json.loads(apps)
                                for key,value in apps_json.items():
                                    if value:
                                        for key2,value2 in value.items():
                                            if value2 and isinstance(value2,list):
                                                for component in value2:
                                                    name=""
                                                    version=""
                                                    cms_obj ={}

                                                    if component.__contains__("name"):
                                                        name=component["name"]
                                                        if name:
                                                            cms_obj["name"]=name.lower()

                                                    if component.__contains__("version"):
                                                        version=component["version"]
                                                        if version:
                                                            cms_obj["version"]=version
                                                    if name:
                                                        cms_obj["source_detail"] = "通过whatruns识别%s" % (name)
                                                        self.web_recongnize_set.append(cms_obj)


        except Exception as e:
            self.marmo_log["exceptions"].append("what runs get data error=="+str(e.__str__()))
            raise Exception("whatruns 获取数据出现异常=="+str(e.__str__()))


    def run(self):
        try:
            self.get_data()
        except Exception as e:
            self.marmo_log["exceptions"].append("what runs get data error==" + str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "WHATRUNS",
                "type": '4',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_id)
            }
            MarmoLogDao().add_log(add_log_params)
            return self.web_recongnize_set


if __name__ =="__main__":
    whatruns = WhatRuns({"domain":"ibao.byfunds.com","srv_type":"https"})
    whatruns.run()






