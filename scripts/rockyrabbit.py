import requests
import time
from urllib.parse import urlparse, parse_qs

from scripts.logger import setup_custom_logger

class RockyRabbitAPI:
    def __init__(self, url, client_id=None):
        self.api_base_url = 'https://api.rockyrabbit.io'
        self.api_endpoints = {
            'account_start': f'{self.api_base_url}/api/v1/account/start',
            'account_init': f'{self.api_base_url}/api/v1/account/init',
            'app_config': f'{self.api_base_url}/api/v1/config',
            'tap': f'{self.api_base_url}/api/v1/clicker/tap',
            'mine_upgrade': f'{self.api_base_url}/api/v1/mine/upgrade',
            'mine_upgrade_sync': f'{self.api_base_url}/api/v1/mine/sync',
            'account_referrals': f'{self.api_base_url}/api/v1/account/referrals',
            'boost_list': f'{self.api_base_url}/api/v1/boosts/list',
            'boost_upgrade': f'{self.api_base_url}/api/v1/boosts',
            'task_list': f'{self.api_base_url}/api/v1/task/list',
            'task_upgrade': f'{self.api_base_url}/api/v1/task/upgrade',
            'update_sponsor': f'{self.api_base_url}/api/v1/account/sponsor',
            'wallet_list': f'{self.api_base_url}/api/v1/wallet',
            'league_data': f'{self.api_base_url}/api/v1/account/level_other',
            'league_user': f'{self.api_base_url}/api/v1/account/level_current'
        }
        self.headers = {}
        self.init_data_raw = ""
        self.cache = {}
        self.active = True
        self.url = url
        self.logger = setup_custom_logger(f"Rocky Rabbit | User: {client_id}")
        self.get_init_data_raw(url)

    def get_init_data_raw(self, url):
        parsed_url = urlparse(url)
        hash_fragment = parsed_url.fragment
        params = parse_qs(hash_fragment)
        self.init_data_raw = params.get("tgWebAppData", [None])[0]
        self.headers = {'Authorization': f'tma {self.init_data_raw}'}
        return self.init_data_raw

    def make_request(self, method: str, url: str, **kwargs) -> dict:
        for _ in range(5):
            try:
                response = requests.request(method, url, headers=self.headers, **kwargs)
                response_data = response.json()
                return response_data
            except Exception as e:
                self.logger.error(f"Exception occurred: {e}")
        return {}

    def account_start(self):
        if not self.active:
            return {}
        if 'account_start' not in self.cache or True:
            response_data = self.make_request('POST', self.api_endpoints['account_start'])
            if not response_data or 'status' in response_data and response_data['status'] != 'ok':
                self.active = False
                self.logger.error(f"Error in account_start: {response_data}")
                return {}
            self.cache['account_start'] = response_data
        return response_data

    def account_init(self, lang="en", sex="male"):
        data = {"lang": lang, "sex": sex}
        return self.make_request('POST', self.api_endpoints['account_init'], json=data)

    def tap(self, count=50):
        data = {"count": count}
        return self.make_request('POST', self.api_endpoints['tap'], json=data)

    def mine_upgrade(self, upgradeId):
        data = {"upgradeId": upgradeId}
        return self.make_request('POST', self.api_endpoints['mine_upgrade'], json=data)

    def mine_upgrade_sync(self):
        return self.make_request('POST', self.api_endpoints['mine_upgrade_sync'])

    def account_referrals(self):
        return self.make_request('POST', self.api_endpoints['account_referrals'])

    def boost_list(self):
        return self.make_request('POST', self.api_endpoints['boost_list'])

    def boost_upgrade(self, boost_id="full-available-taps"):
        data = {"boostId": boost_id}
        return self.make_request('POST', self.api_endpoints['boost_upgrade'], json=data)

    def task_list(self):
        return self.make_request('POST', self.api_endpoints['task_list'])

    def task_upgrade(self, task_id):
        data = {"taskId": task_id}
        return self.make_request('POST', self.api_endpoints['task_upgrade'], json=data)

    def update_sponsor(self, sponsor_id):
        data = {"sponsorId": sponsor_id}
        return self.make_request('POST', self.api_endpoints['update_sponsor'], json=data)

    def wallet_list(self):
        return self.make_request('POST', self.api_endpoints['wallet_list'])

    def league_data(self, level):
        data = {"level": level}
        return self.make_request('POST', self.api_endpoints['league_data'], json=data)

    def league_user(self):
        return self.make_request('POST', self.api_endpoints['league_user'])
    
    def balance(self):
        if not 'account_start' in self.cache:
            self.account_start()
        return self.cache['account_start']['clicker']['balance']
    
    def profit(self):
        if not 'account_start' in self.cache:
            self.account_start()
        return self.cache['account_start']['clicker']['earnPassivePerHour']

    def calculate_refill_time(self, account_data):
        max_taps = account_data['clicker']['maxTaps']
        available_taps = account_data['clicker']['availableTaps']
        taps_recover_per_sec = account_data['clicker']['tapsRecoverPerSec']
        
        taps_needed = max_taps - available_taps
        if taps_recover_per_sec > 0:
            time_to_refill = taps_needed / taps_recover_per_sec
        else:
            time_to_refill = float('inf')

        return time_to_refill
    
    def do_daily_tasks(self):
        upgrades = self.mine_upgrade_sync()
        for upgrade in upgrades:
            if upgrade['type'] == 'daily' and time.time() - upgrade['lastUpgradeAt'] > 24*60*60:
                result = self.mine_upgrade(upgrade['upgradeId'])
                if 'clicker' in result:
                    self.logger.info(f"[+] Task: {upgrade['upgradeId']} | Balance: {result['clicker']['balance']}")
                else:
                    self.logger.error(f"[-] Error in task: {upgrade['upgradeId']} | clicker data not found")
    
    def auto_upgrade(self):
        upgrades = self.mine_upgrade_sync()
        account_level   = self.cache['account_start']['account']['level']
        account_balance = self.cache['account_start']['clicker']['balance']
        
        profitable_upgrades = [
            upgrade for upgrade in upgrades 
            if upgrade.get('profitPerHourDelta', 0) > 0 and upgrade['type'] == 'level-up'
        ]
        
        profitable_upgrades.sort(key=lambda x: x['price'] / x['profitPerHourDelta'])
                
        relevant_upgrades = [
            upgrade for upgrade in upgrades 
            if (upgrade['upgradeId'].endswith('_fighter') or upgrade['upgradeId'].endswith('_coach'))
            and upgrade['level'] <= account_level 
            and upgrade['type'] == 'level-up'
            and upgrade['price'] <= account_balance
        ]
        
        insufficient_balance = False
        
        while not insufficient_balance:
            if not relevant_upgrades:
                break
            b = False
            for upgrade in relevant_upgrades:
                if upgrade['type'] == 'level-up' and upgrade['level'] <= account_level:
                    self.logger.info(f"Upgrade: {upgrade}")
                    upgrade_result = self.mine_upgrade(upgrade['upgradeId'])
                    self.logger.info(f"Upgrade Result: {upgrade_result}")
                    
                    if upgrade_result.get('status') == True:
                        b = True
                        self.logger.info(f"[+] Upgrade: {upgrade['upgradeId']}")
                        break
                    
                    if upgrade_result.get('message') == 'insufficient balance for clicker':
                        self.logger.info(f"[-] {upgrade_result['message']}")
                        insufficient_balance = True
                        break
            if not b:
                break
        
        while not insufficient_balance:
            upgrade_result = self.mine_upgrade(f"league_{account_level}")            
            if upgrade_result.get('status') == True:
                self.logger.info(f"[+] Upgrade: {upgrade['upgradeId']}")
            
            elif upgrade_result.get('message') == 'insufficient balance for clicker':
                self.logger.info(f"[-] {upgrade_result['message']}")
                insufficient_balance = True
                break
            elif upgrade_result.get('message') == 'upgrade task required upgrade':
                self.logger.info(f"[-] {upgrade_result['message']}")
                break
    
    def tap_all(self):
        account_start_data = self.account_start()
        if 'initAccount' in account_start_data and account_start_data['initAccount'] == False:
            self.account_init()
        if not 'clicker' in account_start_data:
            self.logger.info(f"{account_start_data}")
            return False
        elif 'message' in account_start_data and 'init data' in account_start_data:
            return "init data"
        if account_start_data['clicker']['availableTaps'] > 0:
            self.logger.info(f"[+] Tapping {account_start_data['clicker']['availableTaps']}/{account_start_data['clicker']['maxTaps']}")
            tap_data = self.tap(account_start_data['clicker']['availableTaps'])
            return self.calculate_refill_time(tap_data)
        return self.calculate_refill_time(account_start_data)
