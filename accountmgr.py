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

           if(!start_loop):
            
                min_account_id = get_min_account_id();
                max_account_id = get_max_account_id();
                cur_account_id = min_account_id;
                start_loop = true;
           
            if(cur_account_id >= 0):
               if(self.monitoraccount(cur_account_id)):

                  cur_account_id = cur_account_id + 1;
                  if(cur_account_id > max_account_id):
                     start_loop = false; 

            time.sleep(1)
    
    def monitoraccount(self,accountid):

        flag = False

        account = get_account_name(accountid)
        if(account == ""):
            return True
	
        flag = update_token(account)
        flag = update_stake(account)

        return flag;                      

    def update_token(self):
       print("update_token"

    def udpate_stake(self):
       print("update_stake")

    def Start(self):
         
         start_loop = False
         min_account_id = 0
         max_account_id = 0
	 cur_account_id = 0
 
         t =threading.Thread(target=self.threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()

    def get_min_account_id(self):

        min = -1

	try:

	    db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "select min(id) from accounts"
	    cursor.execute(sql)
            
            for row in cursor.fetchall():
                min = row[0]

         except:
            print("get_min_account_id error")
         
         return min

    def get_max_account_id(self):

        max = -1

        try:

            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "select max(id) from accounts"
            cursor.execute(sql)

            for row in cursor.fetchall():
                max = row[0]

         except:
            print("get_max_account_id error")
         
         return max

    def get_account_name(self,accoutid):
         
       account = ""
       try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "select name from accounts where id=%d" %(accountid)
            cursor.execute(sql)
            
            for row in cursor.fetchall():
                account = row[0]
       except:
            print("get_account_name error")

       return account                          
