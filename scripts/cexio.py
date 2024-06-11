import requests
import urllib
import time
from datetime import datetime

from scripts.logger import setup_custom_logger

class Cex_IO:
    def __init__(self, url, admin:int=1):
        
        self.logger  = setup_custom_logger(f"CexIO | User: {admin}")
        
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

    def request_to_backend(self, endpoint, payload, max_retries=3):
        for attempt in range(max_retries):
            try:
                r = self.session.post(endpoint, json=payload).json()
                if r.get('status') == 'ok':
                    return r
                else:
                    self.logger.error(f"Error in response: {r}")
                    return r
            except requests.RequestException as e:
                self.logger.error(f"Request error: {e}")
            except ValueError as e:
                self.logger.error(f"JSON decoding error: {e}")
            time.sleep(2)  # Wait before retrying
        return None

    def getUserInfo(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios"
        }
        endpoint = 'https://cexp.cex.io/api/getUserInfo'
        return self.request_to_backend(endpoint, payload)
    
    def balance(self):
        r = self.getUserInfo()
        if r:
            return r['data']['balance']
        return None
    
    def startTask(self, taskId:str):
        payload = {
            "authData": self.authData,
            "data":{
                "taskId": taskId
            },
            "devAuthData": self.admin,
        }
        endpoint = 'https://cexp.cex.io/api/startTask'
        r = self.request_to_backend(endpoint, payload)
        
        if r and r.get('status') == 'ok':
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
        endpoint = 'https://cexp.cex.io/api/checkTask'
        r = self.request_to_backend(endpoint, payload)
        
        if r and (r['status'] == 'ok' or ('reason' in r['data'] and r['data']['reason'] == 'Task is not at ReadyToCheck state')):
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
        endpoint = 'https://cexp.cex.io/api/claimTask'
        r = self.request_to_backend(endpoint, payload)
        
        if r and r.get('status') == 'ok' and 'claimedBalance' in r['data']:
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
        endpoint = 'https://cexp.cex.io/api/claimTaps'
        return self.request_to_backend(endpoint, payload)
    
    def startFarm(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
        }
        endpoint = 'https://cexp.cex.io/api/startFarm'
        return self.request_to_backend(endpoint, payload)
    
    def claimFarm(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
        }
        endpoint = 'https://cexp.cex.io/api/claimFarm'
        return self.request_to_backend(endpoint, payload)
    
    def farmEndsAt(self):
        try:
            data = self.getUserInfo()
            if data:
                date_string = data['data']['farmStartedAt']
                date_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
                timestamp = date_obj.timestamp() + (60*60*4) + (60*5)
                
                self._farms_end_time = timestamp
                return timestamp - time.time()
            else:
                self.logger.error("Failed to get user info for farm end time.")
                return 0
        except Exception as e:
            self.logger.error(f"Error calculating farm end time: {e}")
            return 0
    
    def farms_end_time(self):
        return self._farms_end_time - time.time()
    
    def check_for_clicks(self):
        r = self.getUserInfo()
        if r:
            availableTaps = r['data']['availableTaps']
            if availableTaps > 0:
                self.claimTaps(availableTaps)
            try:
                if self.farmEndsAt() < 1:
                    self.claimFarm()
                    self.startFarm()
            except Exception as e:
                self.logger.warning("[!] Error in Cex_IO:check_for_clicks: " + str(e))
        else:
            self.logger.error("Failed to get user info for checking clicks.")
    
    def do_tasks(self):
        r = self.getUserInfo()
        if r:
            self.check_for_clicks()
            for task in r['data']['tasks']:
                if r['data']['tasks'][task]['state'] != "Claimed":
                    self.startTask(task)
            time.sleep(60)
            for task in r['data']['tasks']:
                if r['data']['tasks'][task]['state'] != "Claimed":
                    self.checkTask(task)
        else:
            self.logger.error("Failed to get user info for doing tasks.")
