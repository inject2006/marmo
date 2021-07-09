#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name marmo_builtwith
__time__ = "2021/6/10 10:44"
import requests
import json
class MarmoBuiltWith():
    def __init__(self,asset_data):
        self.url ="https://api.builtwith.com/v19/api.json?KEY=%s&LOOKUP=%s"
        self.api_key="15984698-9a17-48bd-a489-bfbfa0fd8138"
        self.asset_data=asset_data
        self.domain=asset_data["domain"]
        self.srv_type=asset_data["srv_type"]
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }


    def get_data(self):
        assert self.api_key
        assert self.domain
        assert self.srv_type
        try:
            lookup = self.srv_type+"://"+self.domain
            url = self.url%(self.api_key,lookup)
            print(url)
            headers =self.headers
            res = requests.get(url,headers=headers)
            if res.status_code ==200:
                result_text = res.text
                if result_text:
                    result_json=json.loads(result_text)
                    if result_json.__contains__("Results"):
                        Results =result_json["Results"]
                        for result in Results:
                            if result and result.__contains__("Result"):
                                Result = result["Result"]
                                if Result and Result.__contains__("Paths"):
                                    Paths = Result["Paths"]
                                    for onePath in Paths:
                                        if onePath and onePath.__contains__("Technologies"):
                                            technologies = onePath["Technologies"]
                                            for technology in technologies:
                                                if technology and technology.__contains__("Name"):
                                                    name = technology["Name"]
                                                    print(name)
        except Exception as e:
            print("builtwith 获取数据出现异常=="+str(e.__str__()))

    def run(self):
        self.get_data()

if __name__ =="__main__":
    marmo_built =MarmoBuiltWith({"domain":"www.nucc.com","srv_type":"https"})
    marmo_built.run()




