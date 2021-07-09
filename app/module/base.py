# -*- coding:UTF-8 -*-

'''
 module基类
'''
import time
import os
from marmo.settings import LOG_PATH
class Base():
    def __init__(self):
        self.headers ={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        self.url=""
        self.config ={

        }
        self.logpath = LOG_PATH

    '''
        写入日志
    '''
    def writeLog(self, log):
        if not os.path.exists(self.logpath):  # 文件夹不存在
            os.mkdir(self.logpath)
        fileName = time.strftime("%Y-%m-%d")
        print(log)
        with open(self.logpath + "/" + fileName + ".log", 'a+', encoding='UTF-8') as f:
            format_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write(format_time + "--------------->" + str(log))
            f.write("\n")
            f.flush()


