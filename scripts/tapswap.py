import requests
import urllib.parse
import json
import time
import random
import cloudscraper
import sys
import js2py

from bs4 import BeautifulSoup
from scripts.BypassTLS import BypassTLSv1_3
from scripts.logger import setup_custom_logger


class TapSwap:
    def __init__(self, url: str, auto_upgrade:bool, max_charge_level:int, max_energy_level:int, max_tap_level:int, client_id:int=1):
        
        self.logger = setup_custom_logger(f"TapSwap | User: {client_id}")
        
        if auto_upgrade:
            self.max_charge_level = max_charge_level
            self.max_energy_level = max_energy_level
            self.max_tap_level    = max_tap_level
        else:
            self.max_charge_level = 1
            self.max_energy_level = 1
            self.max_tap_level    = 1
        
        
        self.webappurl         = url
        self.init_data         = urllib.parse.unquote(url).split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
        self.x_cv              = "615"
        self.access_token      = ""
        self.update_token_time = 0
        
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13; iPhone 15 Pro Max) AppleWebKit/533.2 (KHTML, like Gecko) Version/122.0 Mobile/15E148 Safari/533.2"
        }
        self.headers_requests = self.headers.copy()
        self.headers_requests.update({
            "Authorization": f"Bearer {self.access_token}",
            "x-cv": self.x_cv,
            "X-App": "tapswap_server",
            "x-bot": "no",
        })

        self.session = requests.Session()
        self.session.mount("https://", BypassTLSv1_3())
        
        self.prepare_prerequisites()
        
        
    def prepare_prerequisites(self):
        uph = self.update_headers()
        if uph == False:
            self.logger.error("[!] We ran into trouble with the updates to the headers! 🚫 The script is stopping.")
            sys.exit()
        
        atk = self.get_auth_token()
        if atk == False:
            self.logger.error("[!] We ran into trouble with the get auth token! 🚫 The script is stopping.")
            sys.exit()
    
    def run_code_and_calculate_result(self, code):
        x = JSCodeProcessor(code)
        return x.execute_js_code()
    
    def extract_chq_result(self, chq):
        len_value = len(chq)
        bytes_array = bytearray(len_value // 2)
        x = 157
        
        for t in range(0, len_value, 2):
            bytes_array[t // 2] = int(chq[t:t + 2], 16)
        
        xored = bytearray(t ^ x for t in bytes_array)
        decoded = xored.decode('utf-8')
        return self.run_code_and_calculate_result(decoded)

    def get_auth_token(self):
        
        payload = {
            "init_data": self.init_data,
            "referrer": ""
        }
        
        if time.time() - self.update_token_time < 30*60:
            return
        
        maxtries = 7

        while maxtries >= 0:
            try:
                
                response = self.session.post(
                    'https://api.tapswap.ai/api/account/login',
                    headers=self.headers,
                    data=json.dumps(payload)
                ).json()
                
                                
                if 'wait_s' in response:
                    sleep_time = response["wait_s"]
                    if sleep_time > 70:
                        maxtries += 1
                        continue
                    self.logger.info(f'[+] Wating {round(sleep_time/10)} seconds to get auth token.')
                    time.sleep(sleep_time/10)
                    continue
                
                if 'chq' in response:
                    chq_result = self.extract_chq_result(response['chq'])
                    payload['chr'] = chq_result
                    self.logger.info("[~] ByPass CHQ:  " + str(chq_result))
                    response = requests.post(
                        'https://api.tapswap.ai/api/account/login',
                        headers=self.headers,
                        data=json.dumps(payload)
                    ).json()
                    
                if not 'access_token' in response:
                    
                    self.logger.warning("[!] There is no access_token in response")
                    
                    time.sleep(3)
                    
                    continue
                        
                    
                
                self.client_id = response['player']['id']
                self.headers_requests['Authorization'] = f"Bearer {response['access_token']}"
                self.balance = response['player']['shares']
                energy_level = response['player']['energy_level']
                charge_level = response['player']['charge_level']
                self._time_to_recharge = (energy_level*500) / charge_level
                
                self.update_token_time = time.time()
                
                self.logger.info("Auth Token fetched successfully.")
                
                try:
                    self.check_update(response)
                except Exception as e:
                    self.logger.warning('[!] Error in upgrade: ' + str(e))
                    
                return response['access_token']
            
            except Exception as e:
                self.logger.warning('[!] Error in auth: ' + str(e))
                time.sleep(3)
            finally:
                maxtries -=1
        
        return False

    def update_headers(self):
        maxtries = 5

        while maxtries >= 0:
            try:
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
                }

                session = requests.Session()
                session.mount("https://", BypassTLSv1_3())
                session.headers = headers
                scraper = cloudscraper.create_scraper(sess=session)
                
                headers_json = scraper.get(f'https://poeai.click/tapswap/headers.json').json()
                
                if 'dont_run_code' in headers_json:
                    continue
                
                self.headers.update(headers_json['login'])
                self.headers_requests.update(headers_json['send_tap'])
                
                return self.headers_requests

            except Exception as e:
                self.logger.warning('[!] Error in update headers: ' + str(e))
                time.sleep(3)
                

            finally:
                maxtries -= 1
        
        return False
    
    def check_update(self, response):
        charge_level = response['player']['charge_level']
        energy_level = response['player']['energy_level']
        tap_level    = response['player']['tap_level']
        shares       = response['player']['shares']

        if charge_level < self.max_charge_level:
            price = 0
            while shares >= price:
                for item in response['conf']['charge_levels']:
                    if item['rate'] == charge_level + 1:
                        price = item['price']
                
                if price > shares or charge_level >= self.max_charge_level:
                    break
                
                self.logger.debug('[+] Updating Charge Level')
                
                self.upgrade_boost('charge')

                shares       -= price
                charge_level += 1
        
        if energy_level < self.max_energy_level:
            price = 0
            while shares >= price:
                for item in response['conf']['energy_levels']:
                    if item['limit'] == (energy_level + 1)*500:
                        price = item['price']
                
                if price > shares or energy_level >= self.max_energy_level:
                    break
                
                self.logger.debug('[+] Updating energy')
                
                self.upgrade_boost('energy')

                shares       -= price
                energy_level += 1
        
        if tap_level < self.max_tap_level:
            price = 0
            while shares >= price:
                for item in response['conf']['tap_levels']:
                    if item['rate'] == tap_level + 1:
                        price = item['price']
                
                if price > shares or tap_level >= self.max_tap_level:
                    break
                
                self.logger.debug('[+] Updating taps')
                
                self.upgrade_boost('tap')

                shares    -= price
                tap_level += 1
            
    def tap_stats(self):
        response = self.session.get(
            'https://api.tapswap.ai/api/stat',
            headers=self.headers_requests,
        ).json()
        return response
    
    def upgrade_boost(self, boost_type: str = "energy"):
        payload = {"type": boost_type}
        response = self.session.post(
            'https://api.tapswap.ai/api/player/upgrade',
            headers=self.headers_requests,
            json=payload
        ).json()
        return response
    
    def apply_boost(self, boost_type: str = "energy"):
        payload = {"type": boost_type}
        response = self.session.post(
            'https://api.tapswap.ai/api/player/apply_boost',
            headers=self.headers_requests,
            json=payload
        ).json()
        return response

    def submit_taps(self, taps: int = 1):
        
        o = int(time.time() * 1000)
           
        result = o * self.client_id
        result = result * self.client_id
        result = result / self.client_id
        result = result % self.client_id
        result = result % self.client_id
        
        content_id = int(result)
        
        payload = {"taps": taps, "time": o}
        
        self.headers_requests['Content-Id'] = str(content_id)

        while True:
            try:
                response = self.session.post(
                    'https://api.tapswap.ai/api/player/submit_taps',
                    headers=self.headers_requests,
                    json=payload
                ).json()
                return response
            except Exception as e:
                self.logger.warning("[!] Error in Tapping:  " + str(e))
                time.sleep(1)
    
    def sleep_time(self, num_clicks):
        
        time_to_sleep = 0
        
        for _ in range(num_clicks):
            time_to_sleep += random.uniform(0.1, 0.7)
        
        return time_to_sleep
    
    def click_turbo(self):
        xtap = self.submit_taps(random.randint(60, 70))
        for boost in xtap['player']['boost']:
            if boost['type'] == 'turbo' and boost['end'] > time.time():
                for _ in range(random.randint(3, 7)):
                    
                    taps = random.randint(80, 86)
                    
                    sleepTime = self.sleep_time(taps)
                    
                    self.logger.debug(f'[~] Sleeping {sleepTime/6} for next tap.')
                    
                    time.sleep(sleepTime/6)
                    
                    self.logger.debug(f'[+] Turbo: {taps} ...')
                    
                    xtap = self.submit_taps(taps)
                    
                    shares = xtap['player']['shares']
                    
                    self.logger.debug(f'[+] Balance : {shares}')
                    
                    self.balance = shares
                
                if boost['cnt'] > 0:
                    
                    self.logger.debug('[+] Activing Turbo ...')
                    
                    self.apply_boost("turbo")
                    
                    self.click_turbo()
    
    def click_all(self):
        
        self.prepare_prerequisites()
        
        
        xtap = self.submit_taps(random.randint(1, 10))
        energy = xtap['player']['energy']
        tap_level = xtap['player']['tap_level']
        energy_level = xtap['player']['energy_level']
        charge_level = xtap['player']['charge_level']
        shares = xtap['player']['shares']
        
        total_taps = 0
        self.logger.info('Starting the clicking process on TapSwap 🔘')
        
        while energy > tap_level*3:
            
            maxClicks = min([round(energy/tap_level)-1, random.randint(66, 84)])
            
            if maxClicks > 1:
                
                sleepTime = self.sleep_time(maxClicks)
                                
                time.sleep(sleepTime)
                
                xtap = self.submit_taps(maxClicks)
                
                energy = xtap['player']['energy']
                
                tap_level = xtap['player']['tap_level']
                
                shares = xtap['player']['shares']
                                
                self.balance = shares
                total_taps   += maxClicks
                
            else:
                break
        
        self.logger.info(f'Clicks were successful! | Total clicks: {total_taps} | Balance growth: (+{total_taps*tap_level})')
        
        for boost in xtap['player']['boost']:
            if boost['type'] == 'energy' and boost['cnt'] > 0:
                self.logger.debug('[+] Activing Full Tank ...')
                self.apply_boost()
                self.click_all()
            
            if boost['type'] == 'turbo' and boost['cnt'] > 0:
                self.logger.debug('[+] Activing Turbo ...')
                self.apply_boost("turbo")
                self.click_turbo()
        
        time_to_recharge = ((energy_level*500)-energy) / charge_level
        return time_to_recharge
    
    def shares(self):
        return self.balance
    
    def time_to_recharge(self):
        return self._time_to_recharge + random.randint(60*1, 60*6)

class JSCodeProcessor:
    def __init__(self, js_code):
        self.js_code = js_code
        self.data = None
        self.codes = {}
        self.code_to_run = ""

    def extract_data(self):
        data = "h['innerHTML']" + self.js_code.split("h['innerHTML']")[1].split('}()));function a()')[0].replace(';', ';\n\n').replace("'+'", '')
        data = data.replace('\\x20', ' ').replace('\\x22', '"')
        self.data = data
        return data

    def parse_html(self):
        if self.data is None:
            self.extract_data()
        soup = BeautifulSoup(self.data, 'html.parser')
        div_elements = soup.find_all('div')
        for div in div_elements:
            if 'id' in div.attrs and '_v' in div.attrs:
                self.codes[div['id']] = div['_v']
        
        return self.codes

    def build_js_code(self):
        if not self.codes:
            self.parse_html()

        cjk = self.data.split('var i=')[1].split(';')[0].split(',')
        code_to_run = "function() {"
        for k, v in self.codes.items():
            if k in cjk[0]:
                i = v
                code_to_run += f"i={v};\n"
            if k in cjk[1]:
                j = v
                code_to_run += f"j={v};\n"

        code_to_run += cjk[2] + ";\n"
        r = 'return ' + self.data.split('return')[1].split(';')[0] + ';}'
        code_to_run += r

        self.code_to_run = code_to_run
        return code_to_run

    def execute_js_code(self):
        if not self.code_to_run:
            self.build_js_code()

        r = js2py.eval_js(self.code_to_run)
        return r()
