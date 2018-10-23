#/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import threading
import time
import requests
import json
import pytz
from config import Config 

class accountMgr(object):

    __instance = None

    def __init__(self):
       pass
     
    def __new__(cls, *args, **kwargs):
       if not accountMgr.__instance:
           accountMgr.__instance = object.__new__(cls,*args, **kwargs)
       return accountMgr.__instance

    def Instance(self):
        return accountMgr.__instance


    def threadFun(self,arg):

       while(True):
            
            #voters = self.requestVoters(self.sartAccount)
            time.sleep(1)
            print("ttt")

    def Start(self):
            
         t =threading.Thread(target=self.threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()
