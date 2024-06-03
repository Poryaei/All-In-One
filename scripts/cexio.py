import requests
import urllib
import time
from datetime import datetime

from scripts.logger import setup_custom_logger

class Cex_IO:
    def __init__(self, url, admin:int):
        
        self.logger  = setup_custom_logger("CexIO")
        
        self.headers = {
            "accept": "/",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        
        self.url             = url
        self.admin           = admin
        self.mining          = True
        self.session         = requests.Session()
        self.session.headers = self.headers
        self.authData        = urllib.parse.unquote(url).split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
        self._farms_end_time = 0

    def getUserInfo(self):
        
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios"
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/getUserInfo', 
            json=payload
        ).json()
        
        return r
    
    def balance(self):
        
        r = self.getUserInfo()
        
        return r['data']['balance']
    
    def startTask(self, taskId:str):
        
        payload = {
            "authData": self.authData,
            "data":{
                "taskId": taskId
            },
            "devAuthData": self.admin,
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/startTask', 
            json=payload
        ).json()
        
        if r['status'] == 'ok':
            self.logger.debug(f'[+] Starting Task: {taskId}')
        
        return r
    
    def checkTask(self, taskId:str):
        
        payload = {
            "authData": self.authData,
            "data":{
                "taskId": taskId
            },
            "devAuthData": self.admin,
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/checkTask', 
            json=payload
        ).json()
        
        if r['status'] == 'ok' or ('reason' in r['data'] and r['data']['reason'] == 'Task is not at ReadyToCheck state'):
            self.logger.debug(f'[+] Claim Task Reward: {taskId}')
            self.claimTask(taskId)
        
        return r
    
    def claimTask(self, taskId:str):
        
        payload = {
            "authData": self.authData,
            "data":{
                "taskId": taskId
            },
            "devAuthData": self.admin,
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/claimTask', 
            json=payload
        ).json()
        
        if r['status'] == 'ok' and 'claimedBalance' in r['data']:
            self.logger.debug(f'[+] Task Reward: {r["data"]["claimedBalance"]}')
        
        return r
        
        

    def claimTaps(self, taps=200):
        payload = {
            "authData": self.authData,
            "data":{
                "taps": taps
            },
            "devAuthData": self.admin,
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/claimTaps', 
            json=payload
        ).json()
        
        return r
    
    def startFarm(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/startFarm', 
            json=payload
        ).json()
        
        return r
    
    def claimFarm(self):
        
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
        }
        
        r = self.session.post(
            'https://cexp.cex.io/api/claimFarm', 
            json=payload
        ).json()
        
        return r
    
    def farmEndsAt(self):
        
        data = self.getUserInfo()
        date_string = data['data']['farmStartedAt']
        date_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        timestamp = date_obj.timestamp() + (60*60*4) + (60*5)
        
        self._farms_end_time = timestamp
        
        return timestamp - time.time()
    
    def farms_end_time(self):
        return self._farms_end_time - time.time()
    
    def check_for_clicks(self):
        
        r = self.getUserInfo()
        availableTaps = r['data']['availableTaps']
        
        if availableTaps > 0:
            self.claimTaps(availableTaps)
        
        try:
            if self.farmEndsAt() < 1:
                self.claimFarm()
                self.startFarm()
        except Exception as e:
            print("[!] Error in Cex_IO:check_for_clicks:  ", e)
    
    def do_tasks(self):
        r = self.getUserInfo()
        
        self.check_for_clicks()
        
        for task in r['data']['tasks']:
            if r['data']['tasks'][task]['state'] != "Claimed":
                self.startTask(task)
        
        time.sleep(60)
        
        for task in r['data']['tasks']:
            if r['data']['tasks'][task]['state'] != "Claimed":
                self.checkTask(task)
