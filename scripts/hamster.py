import requests
import urllib
import time
import random

from scripts.logger import setup_custom_logger

class HamsterCombat():
    def __init__(self, url, max_days_for_return:int) -> None:
        
        self.url      = url
        self.mining   = False
        self.maxtries = 10
        self.logger   = setup_custom_logger("Hamster")
        self.token    = self.authToken(self.url)
        self.headers  = {
            "accept": "/",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        
        self.max_days_for_return = max_days_for_return
        
        self.select_exchange()
        
        
        
    
    def wait_time(self, maxTaps:int, availableTaps:int, tapsRecoverPerSec:int):
        return round((maxTaps-availableTaps)/tapsRecoverPerSec)
    
    def authToken(self, url):
        
        payload = {
            "initDataRaw": urllib.parse.unquote(url).split('tgWebAppData=')[1].split('&tgWebAppVersion')[0],
            "fingerprint": {}
        }
        
        maxtries = self.maxtries
        
        while maxtries >= 0:
            try:
                response = requests.post(
                    'https://api.hamsterkombat.io/auth/auth-by-telegram-webapp', 
                    json=payload
                ).json()
                
                return response['authToken']
            except Exception as e:
                
                self.logger.warning("[!] Error in fetching Auth Token. Retrying ")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        return False
                
    def select_exchange(self, exchangeId:str="bingx"):
        
        payload = {
            "exchangeId":exchangeId
        }
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
                
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/select-exchange', 
                    json=payload, 
                    headers=self.headers
                ).json()
                return response
            
            except Exception as e:
                
                self.logger.warning("[!] Error in select exchange")
                
                time.sleep(3)
            
            finally:
                
                maxtries -= 1
        
        return False   
    
    def claim_daily_combo(self):
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
                
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/claim-daily-combo', 
                    headers=self.headers
                ).json()
                
                return response
            
            except Exception as e:
                
                self.logger.warning("[!] Error in claim the daily combo")
                
                time.sleep(3)
            
            finally:
                
                maxtries -= 1

        return False
    
    def buy_boost(self, boostId:str, timex=time.time()*1000):
        
        payload = {
            "boostId":boostId,
            "timestamp":timex
        }
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
                
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/buy-boost', 
                    json=payload, 
                    headers=self.headers
                ).json()
                
                return response
            
            except Exception as e:
                
                self.logger.warning("[!] Error in purchasing Boost")
                
                time.sleep(3)
            
            finally:
                
                maxtries -= 1
        
        return False
    
    def buy_upgrade(self, upgradeId:str, timex=time.time()*1000):
        
        payload = {
            "upgradeId":upgradeId,
            "timestamp":timex
        }
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
                
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/buy-upgrade', 
                    json=payload, 
                    headers=self.headers
                ).json()
                        
                return response
            
            except Exception as e:
            
                self.logger.warning("[!] Error in purchasing Upgrade")
                
                time.sleep(3)
            
            finally:
                
                maxtries -= 1
        
        return False
    
    def balanceCoins(self):
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
            
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/sync', 
                    headers=self.headers
                ).json()
                
                return response['clickerUser']['balanceCoins']
            
            except Exception as e:
                
                self.logger.warning("[!] Error in retrieving account balance.")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        return False
    
    
    def info(self):
        """ id, totalCoins, balanceCoins, level, availableTaps, lastSyncUpdate, exchangeId, referralsCount, maxTaps, earnPerTap, earnPassivePerSec, earnPassivePerHour, lastPassiveEarn, tapsRecoverPerSec """
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
            
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/sync', 
                    headers=self.headers
                ).json()
                
                return response['clickerUser']
            
            except Exception as e:
                
                self.logger.warning("[!] Error in retrieving account info.")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        
        return False
    
    def tap(self, count:int, availableTaps:int=5500, timex=time.time()*1000):
        
        payload = {
            "count":count,
            "availableTaps":availableTaps,
            "timestamp":timex
        }
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
        
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/tap', 
                    json=payload, 
                    headers=self.headers
                ).json()
                
                return response
            
            except Exception as e:
                
                self.logger.warning("[!] Error in submit taps")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        return False
            
    
    def check_boosts(self):
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
        
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/boosts-for-buy',
                    headers=self.headers
                ).json()

                break
            
            except Exception as e:
                
                self.logger.warning("[!] Error in checking boosts")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        for boost in response['boostsForBuy']:
            if boost['id'] == 'BoostFullAvailableTaps' and boost['cooldownSeconds'] == 0 and boost['maxLevel'] - boost['level'] > 0:
                response = self.buy_boost('BoostFullAvailableTaps')
                return True
            
        return False
    
    def upgrade_item(self, upgrade_name:str):
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
        
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/upgrades-for-buy', 
                    headers=self.headers
                ).json()
                
                break
            
            except Exception as e:
                
                self.logger.warning("[!] Error in upgrade items")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        
        
        upgrades = response['upgradesForBuy']
        
        for upgrade_to_buy in upgrades:
            if upgrade_name.lower() in upgrade_to_buy['name'].lower():
                response = self.buy_upgrade(upgrade_to_buy['id'])
                if 'error_code' in response:
                    return False, response['error_message']
                try:
                    for item in response['clickerUser']['upgrades']:
                        if item == upgrade_to_buy['id']:
                            return response['clickerUser']['upgrades'][item]['level']
                except Exception as e:
                    self.logger.warning("[!] Error in upgrade item: " + str(e))
                    return False

        
        return False
        
    
    def find_upgrade_level(self, upgrades, upgrade_id):
        
        for u in upgrades:
            if u['id'] == upgrade_id:
                return u['level'] - 1, u['price']
        return False
    
    def find_best_upgrades(self, upgrades, current_balance, time_horizon=2):
        
        best_upgrades = []
        for upgrade in upgrades:
            if upgrade['isAvailable'] and not upgrade['isExpired']:
                try:
                    hours_to_recoup = upgrade['price'] / (upgrade['profitPerHourDelta'])
                except:
                    continue
                if hours_to_recoup <= time_horizon * 24:
                    x_day_return = upgrade['profitPerHourDelta'] * 24 * time_horizon
                    upgrade['x_day_return'] = x_day_return - upgrade['price']
                    best_upgrades.append(upgrade)
        best_upgrades.sort(key=lambda upgrade: upgrade['x_day_return'], reverse=True)
        return best_upgrades[:3]
    
    def best_upgrades(self):
        
        maxtries = self.maxtries
        
        while maxtries > 0:
            
            try:
        
                response = requests.post(
                    'https://api.hamsterkombat.io/clicker/upgrades-for-buy', 
                    headers=self.headers
                ).json()
                
                break
            
            except Exception as e:
                
                self.logger.warning("[!] Error in best upgrades")
                
                time.sleep(6)
            
            finally:
                
                maxtries -= 1
        
        
        
        upgrades = response['upgradesForBuy']
        updates = []
        balance = self.balanceCoins()
        for i in range(1, self.max_days_for_return):
            sorted_upgrades = self.find_best_upgrades(upgrades, balance, i)
            if len(sorted_upgrades) != 0:
                break
        
        
        for upgrade_to_buy in sorted_upgrades:
            
            if 'cooldownSeconds' in upgrade_to_buy and upgrade_to_buy['cooldownSeconds'] > 0:
                
                self.logger.debug('[~] Continue update for cool down:  ' + upgrade_to_buy['id'])
                
                continue
            
            if upgrade_to_buy['condition'] != None and upgrade_to_buy['condition']['_type'] == 'ByUpgrade':
                
                uid = upgrade_to_buy['condition']['upgradeId']
                
                ulevel = upgrade_to_buy['condition']['level']
                
                xlevel, xprice = self.find_upgrade_level(upgrades, uid)
                
                if xlevel > ulevel:
                    
                    if balance < upgrade_to_buy['price']:
                        continue
                    
                    self.logger.debug('[~] Updating: ' + upgrade_to_buy['id'] + ' | x_day_return: ' + str(upgrade_to_buy['x_day_return']))
                    
                    response = self.buy_upgrade(upgrade_to_buy['id'])
                    
                    updates.append(upgrade_to_buy)
                    
                    balance -= upgrade_to_buy['price']
                    
                else:
                    
                    for i in range((ulevel-xlevel)+1):
                        
                        if balance < xprice:
                            break
                        
                        self.logger.debug('[~] Updating: ' + uid + ' | Need for: ' + upgrade_to_buy['id'])
                        
                        response = self.buy_upgrade(uid)
                        
                        balance -= xprice
                        
            else:
                
                if balance < upgrade_to_buy['price']:
                    continue
                
                self.logger.debug('[~] Updating: ' + upgrade_to_buy['id'] + ' | x_day_return: ' + str(upgrade_to_buy['x_day_return']))
                
                response = self.buy_upgrade(upgrade_to_buy['id'])
                
                updates.append(upgrade_to_buy)
                
                balance -= upgrade_to_buy['price']
                
        self.logger.debug(f'[~] Updated:  {len(updates)}')
        
        return updates
    
    def update_all(self):
        while len(self.best_upgrades()) > 0:
            pass
        return
    
    def auto_tap(self):
        
        taps = self.tap(1)
        
        maxTaps           = taps['clickerUser']['maxTaps']
        availableTaps     = taps['clickerUser']['availableTaps']
        tapsRecoverPerSec = taps['clickerUser']['tapsRecoverPerSec']
        self.sleep_time   = self.wait_time(maxTaps, availableTaps, tapsRecoverPerSec)
        
        if maxTaps - availableTaps > 10:
            self.logger.debug('[~] Wait for full charge')
            return
        
        while availableTaps > 10:
            
            x = random.randint(90, 240)
            if x > availableTaps:
                x = availableTaps
            
            self.logger.debug(f'[~] Tapping {x} Times')
            
            taps          = self.tap(x, availableTaps)
            availableTaps = taps['clickerUser']['availableTaps']
            balanceCoins  = taps['clickerUser']['balanceCoins']
            
            self.logger.debug('[+] Available Taps: ' + str(availableTaps))
            self.logger.debug('[+] Balance Coins: ' + str(round(balanceCoins, 3)))
            
            time.sleep(random.randint(1, 2))
        
        self.sleep_time = self.wait_time(maxTaps, availableTaps, tapsRecoverPerSec)
    
    def start(self):
        
        self.mining       = True
        self.start_time   = time.time()
        self.update_check = 0
        
        while self.mining:
            try:
                self.auto_tap()
            except Exception as e:
                self.logger.warning('[!] Error in start auto tap loop:  ' + str(e))
            
            try:
                if time.time() - self.update_check > (3600)*3:
                    self.best_upgrades()
                    self.update_check = time.time()
                
                if self.check_boosts() == False:
                    self.logger.debug(f'[~] Sleeping {self.sleep_time} Seconds ...')
                    time.sleep(self.sleep_time)
                
            except Exception as e:
                self.logger.warning('[!] Error: ' + str(e))
    
    def stop(self):
        self.mining = False

