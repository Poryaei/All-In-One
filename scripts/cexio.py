import requests
import urllib
import time
import json
import random

from datetime import datetime

from scripts.logger import setup_custom_logger

with open('cexio.json') as f:
    cards_data = json.load(f)

class Cex_IO:
    def __init__(self, url, admin:int=1):
        
        self.logger  = setup_custom_logger(f"CexIO | User: {admin}")
        
        self.headers = {
            "authority": "cexp.cex.io",
            "method": "POST",
            "path": "/api/v2/getUserInfo",
            "scheme": "https",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "origin": "https://cexp.cex.io",
            "priority": "u=1, i",
            "referer": "https://cexp.cex.io/",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "x-appl-version": "0.8.0",
            "x-request-userhash": "",
        }
        
        self.url             = url
        self.admin           = admin
        self.mining          = True
        self.session         = requests.Session()
        self.session.headers = self.headers
        self.authData        = urllib.parse.unquote(url).split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
        self._farms_end_time = 0
        self.user_hash       = self.authData.split('hash=')[1]
        self.headers["x-request-userhash"] = self.user_hash

    def request_to_backend(self, endpoint, payload, max_retries=3):
        for attempt in range(max_retries):
            try:
                r = self.session.post(endpoint, json=payload)
                r = r.json()
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
            "platform": "ios",
            "platform": "ios"
        }
        endpoint = 'https://cexp.cex.io/api/v2/getUserInfo'
        return self.request_to_backend(endpoint, payload)
    
    def getUserCards(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
            "platform": "ios"
        }
        endpoint = 'https://cexp.cex.io/api/v2/getUserCards'
        return self.request_to_backend(endpoint, payload)
    
    def claimMultiTaps(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
            "platform": "ios"
        }
        endpoint = 'https://cexp.cex.io/api/v2/claimMultiTaps'
        return self.request_to_backend(endpoint, payload)
    
    def balance(self):
        r = self.getUserInfo()
        if r:
            return int(r['data']['balance_BTC'])/10000, float(r['data']['balance_USD'])
        return None
    
    def startTask(self, taskId:str):
        payload = {
            "authData": self.authData,
            "data":{
                "taskId": taskId
            },
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/startTask'
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
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/checkTask'
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
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/claimTask'
        r = self.request_to_backend(endpoint, payload)
        
        if r and r.get('status') == 'ok' and 'claimedBalance' in r['data']:
            self.logger.debug(f'[+] Task Reward: {r["data"]["claimedBalance"]}')
        
        return r

    def claimTaps(self, taps=3, tapsEnergy=1000):
        payload = {
            "authData": self.authData,
            "data":{
                "tapsEnergy": f"{tapsEnergy-taps}",
                "tapsToClaim": f"{taps}",
                "tapsTs": int(time.time()*1000)
            },
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/claimMultiTaps'
        return self.request_to_backend(endpoint, payload)
    
    def claimCrypto(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/claimCrypto'
        return self.request_to_backend(endpoint, payload)
    
    def passOnboarding(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/passOnboarding'
        return self.request_to_backend(endpoint, payload)
    
    def buyUpgrade(self, categoryId, upgradeId, nextLevel, cost, effect, effectCcy="CEXP"):
        payload = {
            "authData": self.authData,
            "data":{
                "categoryId": categoryId,
                "upgradeId": upgradeId,
                "nextLevel": nextLevel,
                "cost": cost,
                "ccy": "USD",
                "effect": effect,
                "effectCcy": effectCcy
            },
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/buyUpgrade'
        return self.request_to_backend(endpoint, payload)
    
    def basic_cards_for_upgrade(self):
        cards = {}
        for k,v in cards_data.items():
            for item in v:
                if item['dependency'] == {} and len(item['levels']) > 0 and item['levels'][0][2] > 0:
                    cards[item['upgradeId']] = item
        
        return cards
    
    def find_card_categoryId(self, card):
        for k,v in cards_data.items():
            for item in v:
                if item['upgradeId'] == card:
                    return k
    
    def buy_upgrades_v2(self, max_lvl=10):
        balance = self.balance()[1]
        user_cards = self.getUserCards().get('cards')
        items_for_buy = []

        for k, v in cards_data.items():
            for item in v:
                if len(item['levels']) > 0 and item['levels'][0][2] > 0:
                    card_id = item['upgradeId']
                    current_lvl = self.check_card_lvl(user_cards, card_id)

                    if current_lvl >= len(item['levels']):
                        continue
                    
                    upgrade_cost = int(item['levels'][current_lvl][0])

                    if balance < upgrade_cost:
                        self.logger.debug(f'Insufficient balance to upgrade card {card_id}. Required: {upgrade_cost}, Available: {balance}')
                        continue
                    
                    # Check dependency
                    if item['dependency']:
                        dependency_id = item['dependency']['upgradeId']
                        dependency_lvl = item['dependency']['level']
                        
                        # Check if we have it or not
                        if self.check_card_lvl(user_cards, dependency_id) >= dependency_lvl:
                            items_for_buy.append(
                                [
                                    self.find_card_categoryId(card_id),
                                    card_id,
                                    current_lvl + 1,
                                    upgrade_cost,
                                    item['levels'][current_lvl][2],
                                ]
                            )
                    else:
                        items_for_buy.append(
                            [
                                self.find_card_categoryId(card_id),
                                card_id,
                                current_lvl + 1,
                                upgrade_cost,
                                item['levels'][current_lvl][2],
                            ]
                        )

        if not items_for_buy:
            self.logger.debug('No more upgrades available or balance is insufficient. Exiting upgrade process.')
            return

        # Sort items for buying
        items_for_buy.sort(key=lambda x: (x[3] / x[4], x[3]))  # Sort by profit-to-cost ratio and then by cost

        for item in items_for_buy[0:3]:
            if balance < item[3]:  # Check balance again before buying
                self.logger.debug(f'Insufficient balance to upgrade card {item[1]}. Required: {item[3]}, Available: {balance}')
                continue
                
            time.sleep(random.uniform(1, 3))
            u = self.buyUpgrade(item[0], item[1], item[2], item[3], item[4])
            if u.get('status', '') == 'ok':
                self.logger.debug(
                    f'Successfully upgraded Card: {item[1]} to Level: {item[2]} | CexPower: {item[4]} | Cost: {item[3]}'
                )
                balance -= item[3]  # Deduct cost after successful upgrade
            else:
                self.logger.warning(
                    f'Upgrade failed for item {item[1]}: {u}. Details: {item}'
                )

        self.logger.debug(f'Update process complete. Current Balance: {int(balance)}')
    
    def buy_upgrades(self, max_lvl=10):
        balance = self.balance()[1]
        basic_cards = self.basic_cards_for_upgrade()
        items_for_buy = []
        
        while True:
            user_cards = self.getUserCards().get('cards')
            items_for_buy.clear()
            
            for card_id, card_info in basic_cards.items():
                if card_id in user_cards:
                    current_lvl = user_cards[card_id]['lvl']
                else:
                    current_lvl = 0
                
                    
                upgrade_cost = int(card_info['levels'][current_lvl][0])
                if balance < upgrade_cost:
                    self.logger.debug(f'Insufficient balance to upgrade card {card_id}. Required: {upgrade_cost}, Available: {balance}')
                    continue
                
                if current_lvl + 1 >= len(card_info['levels']):
                    self.logger.debug(f'No available levels to upgrade card {card_id}. Current Level: {current_lvl}')
                    continue
                
                balance -= upgrade_cost
                
                if current_lvl < max_lvl:
                    items_for_buy.append(
                        [
                            self.find_card_categoryId(card_id),
                            card_id,
                            current_lvl + 1,
                            upgrade_cost,
                            card_info['levels'][current_lvl][2],
                        ]
                    )

            if not items_for_buy:
                self.logger.debug('No more upgrades available or balance is insufficient. Exiting upgrade process.')
                break

            for item in items_for_buy:
                time.sleep(random.uniform(1, 3))
                u = self.buyUpgrade(item[0], item[1], item[2], item[3], item[4])
                if u.get('status', '') == 'ok':
                    self.logger.debug(
                        f'Successfully upgraded Card: {item[1]} to Level: {item[2]} | CexPower: {item[4]} | Cost: {item[3]}'
                    )
                else:
                    self.logger.warning(
                        f'Upgrade failed for item {item[1]}: {u}. Details: {item}'
                    )

        self.logger.debug(f'Update process complete. Current Balance: {int(balance)}')
        return items_for_buy

    def getConvertData(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/getConvertData'
        return self.request_to_backend(endpoint, payload)
    
    def convertBalance(self, count):
        price = self.getConvertData().get('convertData', {}).get('lastPrices', [])[-1]
        payload = {
            "authData": self.authData,
            "data":{
                "fromCcy": "BTC",
                "toCcy": "USD",
                "fromAmount": f"{count}",
                "price": f"{price}"
            },
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/convert'
        return self.request_to_backend(endpoint, payload)
    
    def startFarm(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/startFarm'
        return self.request_to_backend(endpoint, payload)
    
    def claimFarm(self):
        payload = {
            "authData": self.authData,
            "data":{},
            "devAuthData": self.admin,
            "platform": "ios",
        }
        endpoint = 'https://cexp.cex.io/api/v2/claimFarm'
        return self.request_to_backend(endpoint, payload)
    
    def check_for_clicks(self):
        r = self.getUserInfo()
        if r:
            try:
                self.claimCrypto()
                user_info = self.balance()
                if not self.admin in [6135970338, "6135970338"] and int(user_info[0]) > 100:
                    self.convertBalance(int(user_info[0])-10)
                    self.buy_upgrades_v2()
                    
                
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
