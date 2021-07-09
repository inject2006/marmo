# -*- coding:UTF-8 -*-
'''
    验证登录
'''
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
import base64
import time
from app.dao.marmo_dao import UserDao
from django.shortcuts import render
from django.conf import settings
class VerifyLoginMiddleware(MiddlewareMixin):

    def __init__(self,get_response):
        super().__init__(get_response)
    '''
        分发请求前拦截请求，并对请求做一个验证
    '''
    def process_request(self,request):
        try:
            print("process request")
            path = request.path
            print(path)
            if "static/" in path or "media" in path:
                print("静态资源访问")
            else:
                if "/login/" not in path:
                    token = request.COOKIES.get("token")
                    if request.session.__contains__("user_id"):
                        user_id = request.session["user_id"]
                        print("user_id=="+str(user_id))
                        if not user_id:
                            '''
                                登录过期
                            '''
                            return HttpResponseRedirect(settings.LOGIN_URL)
                    else:
                        return HttpResponseRedirect(settings.LOGIN_URL)

                    if token:
                        if self.check_token(token):
                            print("验证通过")
                        else:
                            return HttpResponseRedirect(settings.LOGIN_URL)
                    else:
                        print("重定向")
                        return HttpResponseRedirect(settings.LOGIN_URL)
        except Exception as e:
            print("登录出现异常==="+str(e.__str__()))
            raise Exception("登录出现异常==="+str(e.__str__()))


    def check_token(self,token):
        try:
            decode_token = base64.b64decode(token.encode("utf-8")).decode("utf-8")
            token_params = decode_token.split("&")
            username = ""
            userpass = ""
            expires = ""
            for param in token_params:
                if "username" in param:
                    username = param.split("=")[1]
                elif "password" in param:
                    userpass = param.split("=")[1]
                elif "expires" in param:
                    expires = param.split("=")[1]
            now = int(time.time())
            if (int(expires)) < now:
                return False
            '''
                查询用户是否存在
            '''
            userdao = UserDao()
            user_exists = userdao.check_user_exists(username, userpass)
            if user_exists:
                print("用户存在")
                return True

        except Exception as e:
            print("check token error==" + str(e.__str__()))
            return False
