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


    def token_threadFun(self,arg):

       while(True):

           if(not self.token_start_loop):
            
                self.token_min_account_id = self.get_min_account_id()
                self.token_max_account_id = self.get_max_account_id()
                self.token_cur_account_id = self.token_min_account_id

                self.token_start_loop = True
                self.init_tokens()

           
           if(self.token_cur_account_id >= 0):
           
	      if(self.update_token_account(self.token_cur_account_id)):

                  self.token_cur_account_id = self.token_cur_account_id + 1
                  if(self.token_cur_account_id > self.token_max_account_id):
                     self.token_start_loop = False 

           time.sleep(0.001)

    def stake_threadFun(self,arg):

       while(True):

           if(not self.stake_start_loop):

                self.stake_min_account_id = self.get_min_account_id()
                self.stake_max_account_id = self.get_max_account_id()
                self.stake_cur_account_id = self.stake_min_account_id

                self.stake_start_loop = True


           if(self.stake_cur_account_id >= 0):

              if(self.update_stake_account(self.stake_cur_account_id)):

                  self.stake_cur_account_id = self.stake_cur_account_id + 1
                  if(self.stake_cur_account_id > self.stake_max_account_id):
                     self.stake_start_loop = False

           time.sleep(0.001)
    
    def update_token_account(self,accountid):

        flag = False

        account = self.get_account_name(accountid)
        if(account == ""):
            return True
	
        flag = self.update_token(account)

        return flag;                      

    def update_stake_account(self,accountid):

        flag = False

        account = self.get_account_name(accountid)
        if(account == ""):
            return True

        flag = self.update_stake(account)

        return flag;

    def update_token(self,account):

       print "update_token",account
       for token in self.tokens:
           self.update_in_token(account,token)  

       return True

    def update_in_token(self,name,token):

	print "update_in_token"
        
        headers = {'content-type': "application/json"}
        url = Config.HTTP_URL + "get_table_rows"
        try:
             token.symbol = "L"
             token.contract_owner = "chengyahong1"
             name = "chengyahong1"

             data = {"scope":name,"code":token.contract_owner,"table":"accounts","json":True,"limit":1,"lower_bound":token.symbol}
             r = requests.post(url,data =json.dumps(data),headers = headers);
             
             if( r.status_code == 200):
                 js = json.loads(r.text)
                 
                 if((not js is None) and (not js["rows"] is None)):

                      for row in js["rows"]:

                         balance   =  row["balance"]
                         balances = balance.split(" ")
                         
                         symbol    =  balances[1].strip()
                         quantity  =  balances[0]
			 print balance
                         if(symbol == token.symbol):
        		     self.save_token(name,symbol, balance,token.symbol_precision,token.contract_owner)
                              
             else:
                 print "update_in_token request error1"
        except:
             print "update_in_token request error2"

    def getTokenNum(self,balance):
       balances = balance.split(" ")
       return float(balances[0].strip())

    def save_token(self,account,symbol,quantity,precision,contract):

       print "save_toke"
       try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()
            print "tttt"
	    ttt = "INSERT INTO tokens (account,symbol ,balance,symbol_precision,contract_owner)"
            print ttt
            sql = "INSERT INTO tokens (account,symbol ,balance,symbol_precision,contract_owner)  VALUES('%s','%s' ,'%s' , %d ,'%s') ON DUPLICATE KEY UPDATE balance='%s',symbol_precision=%d" %(account,symbol,quantity,precision,contract,quantity,symbol_precision)
            
            print sql
            cursor.execute(sql)
            
            db.commit()

            cursor.close()
            db.close()

       except:
            print("save_token error")
	     
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
                  print cpu_used,cpu_available,cpu_available      

	          net_used      = js["net_limit"]["used"]
                  net_available = js["net_limit"]["available"]
                  net_limit     = js["net_limit"]["max"]

                  ram_quota     = js["ram_quota"]
                  ram_usage     = js["ram_usage"]

                  
		  if( "core_liquid_balance" in js):
                      if(not js["core_liquid_balance"] is None):
                          liquid = self.getTokenNum(js["core_liquid_balance"]) * 10000
                  if("total_resources" in js):
                      total_resources = js["total_resources"]
                      if(not total_resources is None):
                         cpu_total = self.getTokenNum(total_resources["cpu_weight"]) * 10000
                               
                      if("self_delegated_bandwidth" in js):
                         if(not js["self_delegated_bandwidth"] is None): 
                             cpu_staked = self.getTokenNum(js["self_delegated_bandwidth"]["cpu_weight"]) * 10000
                             cpu_delegated = cpu_total - cpu_staked
                         
                      else:
                         cpu_delegated = cpu_total
		
                  
                  if("total_resources" in js):
                      total_resources = js["total_resources"]
                      if(not total_resources is None):
                         net_total = self.getTokenNum(total_resources["net_weight"]) * 10000
                        
                      if("self_delegated_bandwidth" in js):
                         if(not js["self_delegated_bandwidth"] is None):
                             net_staked  = self.getTokenNum(js["self_delegated_bandwidth"]["net_weight"]) * 10000
                             net_delegated = net_total - net_staked
                      else:
                          net_delegated = net_total

                                    
		  if("refund_request" in js):
                      if(not js["refund_request"] is None):
                          net = self.getTokenNum(js["refund_request"]["net_amount"])  * 10000
                          cpu = self.getTokenNum(js["refund_request"]["cpu_amount"]) * 10000
                          unstaking = net + cpu

		                    
            	  staked = cpu_staked + net_staked;
                  total = staked + unstaking + liquid;
                                    
		  if("voter_info" in js):
                        if(not js["voter_info"] is None):
                            total_stake = js["voter_info"]["staked"]

                  totalasset = total_stake + unstaking + liquid
                  
                  self.save_stake(account,liquid ,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_staked,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage)
       
       except:
           print "update stakes error"

       return True

    def save_stake(self,account,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage):
        print("save stake")

        try:
            print account,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "INSERT INTO stakes (account,liquid ,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_staked,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage)  VALUES( '%s',%d ,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d ) ON DUPLICATE KEY UPDATE liquid=%d ,staked=%d,unstaking=%d,total=%d,total_stake=%d,totalasset=%d,cpu_total=%d,cpu_staked=%d,cpu_delegated=%d,cpu_used=%d,cpu_available=%d,cpu_limit=%d,net_total=%d,net_staked=%d,net_delegated=%d,net_used=%d,net_available=%d,net_limit=%d,ram_quota=%d,ram_usage=%d " %(account,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage,liquid,staked,unstaking,total,total_stake,totalasset,cpu_total,cpu_staked,cpu_delegated,cpu_used,cpu_available,cpu_limit,net_total,net_stake,net_delegated,net_used,net_available,net_limit,ram_quota,ram_usage)
            cursor.execute(sql)         
            db.commit()
	    
            cursor.close()
            db.close()
        except:
            print("save stake error")

    def Start(self):
        self.start_stake()
        self.start_token()

    def start_stake(self):
         
         self.stake_start_loop = False
         self.stake_min_account_id = 0
         self.stake_max_account_id = 0
	 self.stake_cur_account_id = 0

         t =threading.Thread(target=self.stake_threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()

    def start_token(self):

         self.token_start_loop = False
         self.token_min_account_id = 0
         self.token_max_account_id = 0
         self.token_cur_account_id = 0
         self.tokens =[]

         t =threading.Thread(target=self.token_threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()

    def init_tokens(self):

        print("init tokens")
        
        try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            sql = "select contract_owner, issuer, symbol_precision, symbol from assets order by id"
            cursor.execute(sql)

            self.tokens = []
            for row in cursor.fetchall():
		token = Token(row[0],row[1],row[2],row[3])
                self.tokens.append(token)

            cursor.close()
            db.close()	
        except:
            print("init_tokens error")

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

