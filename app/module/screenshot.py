# -*- coding:UTF-8 -*-
'''
    利用无头浏览器进行截图操作
    注意参数 image_url,image_path,excute_path
    web信息抓取
'''
from selenium import webdriver
import os
import time
from base64 import b64encode
from marmo.settings import EXECUTE_PATH,IMAGE_PATH,IMAGE_URL
from app.dao.web_asset_dao import WebAssetDao
import json
from app.dao.marmo_log_dao import MarmoLogDao
from app.dao.component_dao import ComponentDao
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class ScreenShot():
    def __init__(self,asset_data):
        self.webdriver =None
        self.excute_path=EXECUTE_PATH
        self.asset = asset_data["asset"]
        self.domain = asset_data["domain"]
        self.port = asset_data["port"]
        self.srv_type =asset_data["srv_type"]
        self.image_url=IMAGE_URL
        self.image_path=IMAGE_PATH
        self.asset_data = asset_data
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
        初始化浏览器
    '''
    def init_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]);
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--headless") #无头
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("window-size=1800,1080")
        # chrome_options.add_argument("--proxy-server=http://42.194.177.125:8999")
        self.webdriver = webdriver.Chrome(executable_path=self.excute_path, chrome_options=chrome_options)
        self.webdriver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                                          Object.defineProperty(navigator, 'webdriver', {
                                            get: () => undefined
                                          })
                                        """
        })
    '''
        访问网站，截图
        output:图片的请求路径
    '''
    def screenshot(self,url,asset_type,asset):
            assert self.webdriver
        # try:
            logger.log("screenshot url ==="+str(url))
            self.marmo_log["datas"].append("screenshot url ==="+str(url))
            self.webdriver.get(url)
            self.webdriver.implicitly_wait(10)
            title=str(self.webdriver.title)
            self.marmo_log["datas"].append("title ===" + str(title))
            response_header ={}
            try:
                response_header=self.get_response_header()
                response_header["Cookies"]=self.get_cookies()
                logger.log(response_header)
            except Exception as e:
                logger.log("网页获取response header出现异常=="+str(e.__str__()))
                self.marmo_log["exceptions"].append("网页获取response header出现异常=="+str(e.__str__()))
            body = self.webdriver.page_source

            if "您的连接不是私密连接" in body and "<title>隐私设置错误</title>" in body:
                self.not_private_link()
            body = self.webdriver.page_source
            logger.log(body)
            body_base64=b64encode(body.encode(encoding="UTF-8")).decode(encoding="UTF-8")
            today = time.strftime("%Y%m%d",time.localtime())
            image_name =str(int(time.time() * 1000))+".png"
            image_dir = os.path.join(self.image_path,str(today))
            if not os.path.exists(image_dir):
                os.system("mkdir -p %s"%(image_dir))
            image_url =str(self.image_url)+"/"+str(today)+"/"+str(image_name)
            self.marmo_log["datas"].append("image url ==" + str(url))
            self.webdriver.save_screenshot(os.path.join(image_dir,image_name))
            '''
                保存数据
            '''
            webassetdao = WebAssetDao()
            add_params = {
                "url": url,
                "status_code": "200",
                "source": 1,
                "source_detail": "通过google浏览器获取",
                "screenshot": image_url,
                "asset_id": self.asset_data["asset_id"],
                "http_ssl_version":"",
                "http_title": title,
                "http_resp_body": body_base64,
                "http_resp_header":json.dumps(response_header),
                "project_id": self.asset_data["project_id"],
                "asset": asset,
                "asset_type": asset_type,
                "url_type": 1,

            }
            webassetdao.add_asset(add_params)
            self.data_info["exists_data"]=True
            self.data_info["status_code"]=2
            self.data_info["data"]=str(add_params)
            # return image_url
        # except Exception as e:
        #     print("网页截图出现异常="+str(e.__str__()))
        #     raise Exception("网页截图出现异常="+str(e.__str__()))
    '''
        获取cookies
    '''
    def get_cookies(self):
            cookie_dict = {}
        # try:
            cookies = self.webdriver.get_cookies()
            if cookies:

                for cookie in cookies:
                    cookie_dict[cookie["name"]]=cookie["value"]
            logger.log("cookie_dict=="+str(cookie_dict))
            self.marmo_log["datas"].append("cookie dict =="+str(cookie_dict))
            return cookie_dict
        # except Exception as e:
        #     print("获取cookies出现异常=="+str(e.__str__()))
        #     return cookie_dict

    '''
        获取response_header
    '''
    def get_response_header(self):
            response_dict={}
        # try:
            js ='''
                            let req = new XMLHttpRequest();
                            req.open('GET', document.location, false);
                            req.send(null);
                            let headers = req.getAllResponseHeaders().toLowerCase();
                            return headers
                    '''
            response_header_string = self.webdriver.execute_script(js)
            self.marmo_log["datas"].append("screenshot get response header=="+str(response_header_string))
            if response_header_string:
                lines = response_header_string.split("\n")
                for line in lines:
                    if line and ":" in line:
                            line_split_string = line.split(":")
                            if "X-Powered-By" in line_split_string[0]:
                                '''
                                    保存到component-tag表
                                '''
                                add_component_tag_params = {
                                    "component_name": line_split_string[1],
                                    "version": "",
                                    "component_type": 0,
                                    "create_source": "from",
                                    "source_detail": "资产进行屏幕截图发现的组件信息X-Power-By",
                                    "project_id": int(self.asset_data["project_id"]),
                                    "description": "资产进行屏幕截图发现的组件信息X-Power-By",
                                    "asset": self.asset_data["asset"]
                                }
                                self.marmo_log["datas"].append("screenshot add componet tag params =="+str(add_component_tag_params))
                                ComponentDao().create_tag(add_component_tag_params)
                            response_dict[line_split_string[0]]=line_split_string[1]
            logger.log("response_dict"+str(response_dict))
            self.marmo_log["response_dict =="+str(response_dict)]
            return response_dict

        # except Exception as e:
        #     print("获取响应头出现异常=="+str(e.__str__()))
        #     return response_dict


    '''
        qidong
    '''
    def run(self):
        try:
            self.init_driver()
            '''
                要根据情况来访问
            '''
            if self.domain and self.port and self.srv_type:
                '''
                    根据域名来访问
                '''
                url=str(self.srv_type)+"://"+str(self.domain)+":"+str(self.port)

                self.marmo_log["datas"].append("screenshot domain url =="+str(url))
                self.screenshot(url,2,self.domain)
            if self.asset and  self.port and self.srv_type:
                url=str(self.srv_type)+"://"+str(self.asset)+":"+str(self.port)
                self.marmo_log["datas"].append("screenshot ip url ==" + str(url))
                self.screenshot(url,1,self.asset)
        except Exception as e:
            logger.log("screenshot error =="+str(e.__str__()))
            self.data_info["status_code"]=3
            self.data_info["exists_data"]=False
            self.data_info["fail_reason"]="屏幕截图出现异常="+str(e.__str__())
            self.marmo_log["exceptions"].append("屏幕截图出现异常="+str(e.__str__()))
        finally:
            if self.webdriver:
                self.webdriver.quit()
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "SCREENSHOT",
                "type": '3',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info

    '''
        不是私密连接
    '''
    def not_private_link(self):
        self.marmo_log["datas"].append("网页出现私密链接")
        button =self.webdriver.find_element_by_id("details-button")
        if button:
            button.click()
            time.sleep(2)
            keep_going =self.webdriver.find_element_by_id("proceed-link")
            if keep_going:
                keep_going.click()
                time.sleep(5)



if __name__ =="__main__":
    screenshot = ScreenShot("http://www.sznzy.cn/","D:/chromedriver.exe",{})
    print(screenshot.run())






