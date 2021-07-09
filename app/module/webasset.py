# -*- coding:UTF-8 -*-
'''
    web资产在线识别
    次数用完结果:"Insufficient credits"
'''
import requests
import time
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
from app.dao.component_dao import ComponentDao
import os
import re
import json
from .marmo_whatruns import WhatRuns
from .shuziguanxing import ShuZiGuanXing
from marmo.settings import CMSEEK_FILE_PATH
from app.dao.marmo_log_dao import MarmoLogDao
from django_redis import get_redis_connection
class WebAsset():
    def __init__(self,asset_data):
        self.asset_data=asset_data
        self.api_url="https://api.wappalyzer.com/lookup/v2/?urls=%s"
        self.whatweb_url="http://whatweb.bugscaner.com/what.go"
        self.acms_command ="/usr/local/bin/python3 /data/ACMSDiscovery/ACMSDiscovery.py -u %s -t 100"
        self.finger_command ="/usr/bin/python2 /data/fingerprint/fingerprint.py %s"
        self.cmseek_command ="/usr/local/bin/python3 /data/CMSeeK/cmseek.py -u %s"
        self.cmsidentifited_command ="/usr/bin/python2 /data/cmsIdentification/cmsIdentification.py %s %s"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }

        self.web_recongnize_set =[]
        self.bugscaner =""
        self.module_name=asset_data["module_name"]
        self.domain = asset_data["domain"]
        self.srv_type = asset_data["srv_type"]
        self.asset = asset_data["asset"]
        self.port =asset_data["port"]
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
        获取wappler的key,从redis中拿
    '''
    def get_redis_wapplayer_key(self,redis_key):
        redis_connections = get_redis_connection("default")
        '''
            默认获取列表第一个值
        '''
        redis_value = redis_connections.lindex(redis_key,0)
        if redis_value:
            if isinstance(redis_value,bytes):
                redis_value = redis_value.decode(encoding="UTF-8")
            return redis_value
        else:
            return  ""

    '''
        删除指定列表的key
    '''
    def del_redis_wapplayer_key(self,redis_key,key):
        redis_connections = get_redis_connection("default")
        redis_connections.lrem(redis_key,1,key)

    '''
        请求wappalyzer
        不支持ip:port形式
        只有通过域名才能获取 
    '''
    def get_data(self,url):
        is_need_next_run=True
        if self.domain:
            while is_need_next_run:
                year = time.strftime("%Y")
                month = time.strftime("%m")
                redis_key = year + "-" + month
                headers = self.headers
                api_key = self.get_redis_wapplayer_key(redis_key)
                if api_key:
                    headers["x-api-key"]=api_key
                    url =self.api_url%(url)
                    logger.log(url)
                    self.marmo_log["datas"].append("get data url =="+str(url))
                    res = requests.get(url,headers=headers)
                    if res.status_code ==200:
                        if "Insufficient credits" in res.text:
                            '''
                                次数用完，删除当前key,重新获取新的key
                            '''
                            logger.log("当前账号次数用完，删除账号")
                            self.marmo_log["datas"].append("当前账号次数用完，删除账号")
                            self.del_redis_wapplayer_key(redis_key,api_key)
                            continue
                        wappaly_json = res.json()
                        logger.log("wappalyzer数据返回=="+str(wappaly_json))
                        self.marmo_log["datas"].append("wappalyzer数据返回=="+str(wappaly_json))
                        for wappaly in wappaly_json:
                            if wappaly.__contains__("technologies"):
                                technologies =wappaly["technologies"]
                                for technology in technologies:
                                    obj ={}
                                    name = technology["name"]
                                    versions = technology["versions"]
                                    if name:
                                        obj["name"] = name
                                    if versions and len(versions)>=1:
                                        obj["versions"]=versions
                                    self.web_recongnize_set.append(obj)
                        is_need_next_run=False
                    else:
                        is_need_next_run=False
                        raise Exception("获取wappalyer数据请求出错==="+str(res.status_code))
    '''
        请求bugscaner,获取第一行的数据,目前网站出现异常,暂时废弃
    '''
    def get_bugscaner_data(self,url):
        headers =self.headers
        headers["Host"]="whatweb.bugscaner.com"
        headers["Origin"]="http://whatweb.bugscaner.com"
        headers["Referer"]="http://whatweb.bugscaner.com/look/"
        headers["X-Requested-With"]="XMLHttpRequest"
        headers["Content-Type"]="application/x-www-form-urlencoded; charset=UTF-8"
        data={
            "url": (None,url),
            "location_capcha": (None,"no")
        }
        bugscan_res =requests.request("POST",self.whatweb_url,files=data)
        if bugscan_res.status_code ==200:
            bugscan_data = bugscan_res.json()
            self.marmo_log["datas"].append("bugscan data  ==" + str(bugscan_data))
            CMS = bugscan_data["CMS"]

            self.bugscaner =bugscan_data
        else:
            logger.log("获取bugscan数据出现异常=="+str(bugscan_res.status_code))
            self.marmo_log["exceptions"].append("获取bugscan数据出现异常=="+str(bugscan_res.status_code))
            # raise Exception("获取bugscan数据出现异常=="+str(bugscan_res.status_code))


    '''
        结果如下所示
        CMS: dedecms , URI: /favicon.ico , Finger MD5: 7ef1f0a0093460fe46bb691578c07c95
        CMS: dedecms , URI: /data/admin/allowurl.txt , Finger MD5: dda6f3b278f65bd77ac556bf16166a0c
        CMS: dedecms , Finger URI: /templets/default/style/dedecms.css
        CMS: dedecms , Finger URI: /include/js/dedeajax2.js
        CMS: dedecms , Finger URI: /data/admin/allowurl.txt
        CMS: dedecms , Finger URI: /data/admin/ver.txt
        CMS: dedecms , Finger URI: /plus/img/wbg.gif
        这个产生的结果是只有组件名称，没有版本信息
    '''
    def run_acms(self,url):
        command = self.acms_command%(url)
        logger.log("acms discovery command =="+str(command))
        self.marmo_log["datas"].append("acms discovery command =="+str(command))
        acms_result =""
        acms_results = os.popen(command)
        for result in acms_results:
            acms_result+=str(result)
        logger.log("acms results ==="+str(acms_result))
        if acms_result:
            pattern ="CMS: (.*?) ,"
            res = re.findall(pattern,acms_result,re.S)
            if res and len(res) >=1:
                temp_set = set()
                for cms in res:
                    if cms:
                        cms_lower = cms.lower()
                        logger.log("ACMS discovery 识别出 %s"%(cms_lower))
                        self.marmo_log["datas"].append("ACMS discovery 识别出 %s"%(cms_lower))
                        temp_set.add(cms_lower)
                for tem_component in temp_set:
                    self.web_recongnize_set.append({"name":tem_component,"version":"","source_detail":"组件是通过acms识别出的"})

    '''
        结果如下所示
        [-]	指纹库已加载11个语言特征
        [-]	指纹库已加载28个Web容器特征
        [-]	指纹库已加载2123个CMS特征
        识别到:nginx,xxxxx
        识别到:dedecms,
        [-]	识别完成, 耗时: 6.460000 
        
    '''
    def run_fingerprint(self,url):
        command = self.finger_command%(url)
        logger.log("finger print command =="+str(command))
        self.marmo_log["datas"].append("finger print command =="+str(command))
        finger_result = ""
        finger_results = os.popen(command)
        for result in finger_results:
            finger_result += str(result)
        logger.log("finger print result =="+str(finger_result))
        if finger_result:
            pattern = "识别到:(.*?),"
            res = re.findall(pattern, finger_result, re.S)
            if res and len(res) >= 1:
                temp_set = set()
                for cms in res:
                    if cms:
                        cms_lower = cms.lower()
                        logger.log("finger print 识别出 %s" % (cms_lower))
                        self.marmo_log["datas"].append("finger print 识别出 %s" % (cms_lower))
                        temp_set.add(cms_lower)
                for temp in temp_set:
                    self.web_recongnize_set.append({"name": temp,"version":"","source_detail":"通过fingerprint识别出来"})

    '''
        结果如下所属
         ┏━Target: nossahphoto.com
         ┃
         ┠── CMS: WordPress
         ┃    │
         ┃    ├── Version: 4.9.18
         ┃    ╰── URL: https://wordpress.org
         ┃
         ┠──[WordPress Deepscan]
         ┃    │
         ┃    ├── Readme file found: https://nossahphoto.com//readme.html
         ┃    ├── License file: https://nossahphoto.com//license.txt
         ┃    │
         ┃    ├── Usernames harvested: 2
         ┃    │    │
         ┃    │    ├── user
         ┃    │    ╰── dhasson
         ┃    │
         ┃
         ┠── Result: /data/CMSeeK/Result/nossahphoto.com/cms.json
         ┃
         ┗━Scan Completed in 45.35 Seconds, using 44 Requests
    默认生成路径:/data/CMSeeK/Result/xxx/cms.json
    '''
    def run_cmseek(self,url):
        command = self.cmseek_command % (url)
        logger.log("cmseek print command ==" + str(command))
        self.marmo_log["datas"].append("cmseek print command ==" + str(command))
        finger_result = ""
        finger_results = os.popen(command)
        for result in finger_results:
            finger_result += str(result)
        logger.log("cmseek results =="+str(finger_result))
        if finger_result:
            '''
                查找路径:
            '''
            file_name =self.find_cmseek_file_path(url)
            if file_name:
                file_path =CMSEEK_FILE_PATH%(file_name)
                self.marmo_log["datas"].append("cmseek file path =="+str(file_path))
                if os.path.exists(file_path):
                    with open(file_path,"r",encoding="UTF-8") as f:
                        results = f.read()
                        self.marmo_log["datas"].append("cmseek results =="+str(results))
                        if results:
                            result_json = json.loads(results)
                            if isinstance(result_json,list):
                                for one_result in result_json:
                                    cms_obj ={}
                                    if one_result.__contains__("cms_name"):
                                        cms_name = one_result["cms_name"]
                                        if cms_name:
                                            cms_obj["name"]=cms_name
                                    if one_result.__contains__("wp_version"):
                                        version = one_result["wp_version"]
                                        if version:
                                            cms_obj["version"]=version
                                    self.web_recongnize_set.add(cms_obj)
                            elif isinstance(result_json,dict):
                                cms_obj = {}
                                if result_json.__contains__("cms_name"):
                                    cms_name = result_json["cms_name"]
                                    if cms_name:
                                        cms_obj["name"] = cms_name
                                if result_json.__contains__("wp_version"):
                                    version = result_json["wp_version"]
                                    if version:
                                        cms_obj["version"] = version
                                self.web_recongnize_set.add(cms_obj)
            # pattern =".*?\[\*\] Version Detected, (.*?) Version (.*?)\[i\].*?"
            # res =re.findall(pattern,finger_result,re.S)
            # if res and len(res) >=1:
            #     for resu in res:
            #         if len(resu) >=2:
            #             logger.log("cmseek 识别出 %s,%s"+str(resu[0],resu[1]))
            #             self.marmo_log["datas"].append("cmseek 识别出 %s,%s"+str(resu[0],resu[1]))
            #             self.web_recongnize_set.append({"name":resu[0],"version":resu[1]})
            #         else:
            #             logger.log("cmseek 识别出 %s" + str(resu))
            #             self.marmo_log["datas"].append("cmseek 识别出 %s" + str(resu))
            #             self.web_recongnize_set.append({"name": resu[0]})


    '''
        必须有domain才行
        
    '''
    def run_what_runs(self,asset_id):
        if self.domain:
            whatruns = WhatRuns(self.domain,self.srv_type,asset_id)
            what_result =whatruns.run()
            self.marmo_log["datas"].append("what run result=="+str(what_result))
            if what_result and len(what_result)>=1:
                for x in what_result:
                    self.web_recongnize_set.append(x)

    '''
        查询cmseek生成的文件路径
    '''
    def find_cmseek_file_path(self,url):
        urls = url.split(":")
        if len(urls) == 3:
            real_url = urls[1] + "_" + str(urls[2])
            real_url = real_url.replace("/", "")
            return real_url
        elif len(urls) == 2:
            real_url = urls[1]
            real_url = real_url.replace("/", "")
            return real_url
    '''
        运行数字观星
    '''
    def run_shuziguanxing(self,url,srv_type,asset_id):
        # if self.domain:
            shuziguanxing = ShuZiGuanXing(url,srv_type,asset_id)
            shuziguanxing_result =shuziguanxing.run()
            self.marmo_log["datas"].append("数字观星识别出==" + str(shuziguanxing_result))
            if shuziguanxing_result and len(shuziguanxing_result) >=1:
                for x in shuziguanxing_result:
                    self.web_recongnize_set.append(x)


    '''
        运行cmsIdentification
        运行5个模式
    '''
    def run_cmsIdentification(self,url):
        mode =["fast","json","thb","holdsword","rapid"]
        for x in mode:
            command = self.cmsidentifited_command%(url,x)
            logger.log("cmsIdentifited command %s"%(command))
            cmsidentifited_result =""
            cms_results = os.popen(command)
            for result in cms_results:
                cmsidentifited_result+=str(result)
            if cmsidentifited_result:
                pattern =".*?target's cms is (.*?)|source.*?"
                res = re.findall(pattern,cmsidentifited_result,re.S)
                if res and len(res) >=1:
                    for cms in res:
                        obj ={}
                        if cms:
                            obj["name"]=cms.lower()
                            obj["version"]=""
                            obj["source_detail"]="通过cmsIdentification 识别到的"
                            self.web_recongnize_set.append(obj)








    '''
        深度识别
        params:
        parma1:url
        param2:srv_type
        param3:asset(domain/ip)
        param4:port
    '''
    def web_recongnize(self,url,srv_type,asset,port):
        self.get_data(url)
        logger.log("getdata")
        # self.get_bugscaner_data(url)
        self.run_acms(url)
        logger.log("acms")
        # self.run_cmseek(url)
        logger.log("cmseek")
        self.run_shuziguanxing(str(asset)+":"+str(port),srv_type,self.asset_data["asset_id"])
        logger.log("shuziguanxing")
        self.run_what_runs(self.asset_data["asset_id"])
        logger.log("whatruns")
        self.run_cmsIdentification(url)
        logger.log("run_cmsIdentification")
        logger.log("web资产识别资产=="+str(self.web_recongnize_set))


    '''
        run函数
    '''
    def run(self):
        try:
            '''
                拼接出正确的url
            '''
            self.marmo_log["datas"].append("run srv type =="+str(self.srv_type))
            if self.domain and self.srv_type and self.port:
                url =str(self.srv_type)+"://"+str(self.domain)+":"+str(self.port)
                self.marmo_log["datas"].append("web asset url ==" + str(url))
                self.web_recongnize(url,self.srv_type,self.domain,self.port)
            if self.asset and self.srv_type and self.port:
                url =str(self.srv_type)+"://"+str(self.asset)+":"+str(self.port)
                self.marmo_log["datas"].append("web asset url ==" + str(url))
                self.web_recongnize(url,self.srv_type,self.asset,self.port)
            exists_data =False
            if len(self.web_recongnize_set) >=1:
                exists_data=True
            if exists_data:
                self.data_info["exists_data"]=True
                self.data_info["status_code"]=2
                self.data_info["data"]=str(self.web_recongnize_set)
            else:
                self.data_info["status_code"]=2
            '''
                插入componet_tag数据
                component_name,version,component_type,create_source,source_detail,project_name,description,asset
            '''
            componentdao = ComponentDao()
            for recongnize in self.web_recongnize_set:
                add_parmas ={
                    "component_name":recongnize["name"],
                    "component_type":2,
                    "create_source":"from",
                    "source_detail":str(self.web_recongnize_set),
                    "project_name":self.asset_data["project_name"],
                    "description":"通过web资产识别 获取到的数据",
                    "asset":self.asset_data["asset"]
                }
                if recongnize.__contains__("version"):
                    add_parmas["version"]=recongnize["version"]
                else:
                    add_parmas["version"]=""

                componentdao.create_tag(add_parmas)

        except Exception as e:
            logger.log("web资产在线识别出现异常=="+str(e.__str__()))
            self.data_info["exists_data"]=False
            self.data_info["status_code"]=3
            self.data_info["fail_reason"]="web资产在线识别出现异常=="+str(e.__str__())
            self.marmo_log["exceptions"].append("web资产在线识别出现异常=="+str(e.__str__()))
            '''
                更新module_function记录
            '''
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "WEB_RECONGNIZE",
                "type": '4',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info






if __name__ =="__main__":
    webasset=WebAsset({"asset":"https://www.kerororo.com","module_name":"wappaler"})
    webasset.run()








