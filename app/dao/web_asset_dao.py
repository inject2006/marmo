# -*- coding:UTF-8 -*-
'''
    web资产操作类
'''
from app.models import WebAsset
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class WebAssetDao():
    def __init__(self):
        pass

    def add_asset(self,data):
        try:
            add_params ={
                "url":data["url"],
                "status_code": data["status_code"],
                "source": data["source"],
                "source_detail": data["source_detail"],
                "screenshot":data["screenshot"],
                "asset_id": data["asset_id"],
                "http_ssl_version": data["http_ssl_version"],
                "http_title": data["http_title"],
                "http_resp_body": data["http_resp_body"],
                "http_resp_header": data["http_resp_header"],
                "project_id": data["project_id"],
                "asset": data["asset"],
                "asset_type": data["asset_type"],
                "url_type": data["url_type"],

            }
            web_asset = WebAsset.objects.create(**add_params)
            if web_asset:
                return True
            else:
                raise Exception("创建web资产失败")
        except Exception as e:
            logger.log("add_asset error=="+str(e.__str__()))
            raise Exception("add_asset error=="+str(e.__str__()))
