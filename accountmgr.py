#/usr/bin/python
# -*- coding: UTF-8 -*-
import MySQLdb
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

           if(not self.start_loop):
            
                self.min_account_id = self.get_min_account_id()
                self.max_account_id = self.get_max_account_id()
                self.cur_account_id = self.min_account_id
                self.start_loop = True

                print self.min_account_id,self.max_account_id
           
           if(self.cur_account_id >= 0):
           
	      if(self.monitoraccount(self.cur_account_id)):

                  self.cur_account_id = self.cur_account_id + 1
                  if(self.cur_account_id > self.max_account_id):
                     self.start_loop = false; 

           time.sleep(1)
    
    def monitoraccount(self,accountid):

        flag = False

        account = self.get_account_name(accountid)
        if(account == ""):
            return True
	
        flag = self.update_token(account)
        flag = self.update_stake(account)

        return flag;                      

    def update_token(self,account):
       print "update_token",account

    def update_stake(self,account):
       print "update_stake",account

    def Start(self):
         
         self.start_loop = False
         self.min_account_id = 0
         self.max_account_id = 0
	 self.cur_account_id = 0
 
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

    def get_account_name(self,accountid):
         
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
