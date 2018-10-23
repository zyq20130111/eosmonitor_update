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

class Token(object):
   def __init__(self,contract_owner,issuer,symbol_precision,symbol):
      self.contract_owner = contract_owner
      self.issuer         = issuer
      self.symbol_precision = symbol_precision
      self.symbol           = symbol

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
                self.init_tokens()

                print self.min_account_id,self.max_account_id
           
           if(self.cur_account_id >= 0):
           
	      if(self.monitoraccount(self.cur_account_id)):

                  self.cur_account_id = self.cur_account_id + 1
                  if(self.cur_account_id > self.max_account_id):
                     self.start_loop = false; 

           time.sleep(0.001)
    
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
       for token in self.tokens:
           self.update_in_token(name,token)  

       return True

    def update_in_token(self,name,token):

	print "update_in_token"
        
        headers = {'content-type': "application/json"}
        url = Config.HTTP_URL + "get_table_rows"
        try:
             start = '"{0}"'.format(token.symbol)
             contract = token.contract_owner
             scope   = name
             r = requests.post(url,data =json.dumps({"scope":scope,"code":contract,"table":"accounts","json":True,"limit":3,"lower_bound":start}),headers = headers);
             
             if( r.status_code == 200):
                 js = json.loads(r.text)
                 
                 if((not js is None) and (not js["rows"] is None)):

                      for row in js["rows"]:

                         balance   =  row["balance"]
                         balances = balance.split(" ")
                         
                         symbol    =  balances[1]
                         quantity  =  balances[0]

                         if(symbol == token.symbol):
        		     self.save_token(name,symbol, balance,token.symbol_precision,token.contract_owner)
                              
             else:
                 print "update_in_token request error1"
        except:
             print "update_in_token request error2"

    def save_token(self,account,symbol,quantity,precision,contract):

       print "save_toke"
       try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()
            sql = "INSERT INTO tokens (account,symbol ,balance,symbol_precision,contract_owner)  VALUES( %s, %s ,%s , %d ,%s ) ON DUPLICATE KEY UPDATE balance=%s,symbol_precision=%d" %(account,symbol,quantity,precision,contract,quantity,symbol_precision)
            cursor.execute(sql)

            cursor.close()
            db.close()

       except:
            print("get_min_account_id error")
	     
    def update_stake(self,account):
       print "update_stake",account

       liquid = 0
       staked = 0
       unstaking = 0
       total = 0;
       totalasset = 0

       cpu_total = 0
       cpu_staked = 0
       cpu_delegated = 0
       cpu_used = 0
       cpu_available = 0
       cpu_limit = 0

       net_total = 0
       net_staked = 0
       net_delegated = 0
       net_used = 0
       net_available = 0
       net_limit = 0

       ram_quota = 0
       ram_usage = 0

       total_stake = 0
       
       headers = {'content-type': "application/json"}
       url = Config.HTTP_URL + "get_account"

       try:
           r = requests.post(url,data =json.dumps({"account_name":account}),headers = headers);
           if( r.status_code == 200):
              js = json.loads(r.text)

              if (not js is None):
                  cpu_used = js["cpu_limit"]["used"]
                  cpu_available = js["cpu_limit"]["available"]
                  cpu_limit     = js["cpu_limit"]["max"]
                  

	          net_used      = js["net_limit"]["used"]
                  net_available = js["net_limit"]["available"]
                  net_limit     = js["net_limit"]["max"]

                  ram_quota     = js["ram_quota"]
                  ram_usage     = js["ram_usage"]

		  if( "core_liquid_balance" in js):
                      liquid = js["core_liquid_balance"]

                  if("total_resources" in js):
                      total_resources = js["total_resources"]
                      if(not total_resources is None):
                         cpu_total = total_resources["cpu_weight"]

                      if("self_delegated_bandwidth" in js):
                         cpu_staked = js["self_delegated_bandwidth"]["cpu_weight"]
                         cpu_delegated = cpu_total - cpu_staked
                      else:
                         cpu_delegated = cpu_total



                  if("total_resources" in js):
                      total_resources = js["total_resources"]
                      if(not total_resources is None):
                         net_total = total_resources["net_weight"]

                      if("self_delegated_bandwidth" in js):
                         net_staked  = js["self_delegated_bandwidth"]["net_weight"]
                         net_delegated = net_total - net_staked
                      else:
                          net_delegated = net_total

		  if("refund_request" in js):
                      net = js["refund_request"]["net_amount"]
                      cpu = js["refund_request"]["cpu_amount"]
                      unstaking = net + cpu

            	  staked = cpu_staked + net_staked;
                  total = staked + unstaking + liquid;

                  url = Config.HTTP_URL + "get_account"
                  r = requests.post(url,data =json.dumps({"scope":"eosio","code":"eosio","table":"voters","json":True,"table_key":"owner","lower_bound":account}),headers = headers);
                  if( r.status_code == 200):
                      js = json.loads(r.text)
                      if(len(js["rows"]) > 0):
                          total_stake = js["rows"][0]["staked"]

                   totalasset = total_stake + unstaking + liquid
                   self.save_stake(account,liquid ,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_staked,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage)
       
       except:
           print "update stakes error"

       return True

    def save_stake(self,account,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage):
        print("init tokens")

        try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "INSERT INTO stakes (account,liquid ,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_staked,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage)  VALUES( %s,%d ,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d ) ON DUPLICATE KEY UPDATE liquid=%d ,staked=%d,unstaking=%d,total=%d,total_stake=%d,totalasset=%d,cpu_total=%d,cpu_staked=%d,cpu_delegated=%d,cpu_used=%d,cpu_available=%d,cpu_limit=%d,net_total=%d,net_staked=%d,net_delegated=%d,net_used=%d,net_available=%d,net_limit=%d,ram_quota=%d,ram_usage=%d " %(account,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage)
            cursor.execute(sql)         
	    
            cursor.close()
            db.close()
        except:
            print("get_min_account_id error")

    def Start(self):
         
         self.start_loop = False
         self.min_account_id = 0
         self.max_account_id = 0
	 self.cur_account_id = 0
         self.tokens =[]

         t =threading.Thread(target=self.threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()

    def init_tokens(self):

        print("init tokens")
        
        try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "select contract_owner, issuer, symbol_precision, symbol from assets order by id"
            cursor.execute(sql)

            self.tokens.clear()
            for row in cursor.fetchall():
		token = Token(row[0],row[1],row[2],row[3])
                self.tokens.append(token)

            cursor.close()
            db.close()	
        except:
            print("get_min_account_id error")

    def get_min_account_id(self):

        min = -1

	try:

	    db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "select min(id) from accounts"
	    cursor.execute(sql)
            
            for row in cursor.fetchall():
                min = row[0]
            
            cursor.close()
            db.close()
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

            cursor.close()
            db.close()

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

            cursor.close()
            db.close()

       except:
            print("get_account_name error")

       return account

