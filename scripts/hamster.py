import requests
import urllib
import time
import random
import base64
import json

import hashlib
from datetime import timezone

try:
    with open('finger.json') as f:
        finger_data = json.load(f)
except:
    finger_data = {}

from datetime import datetime, timedelta
from scripts.logger import setup_custom_logger
                    
class HamsterCombat:
    def __init__(self, url, max_days_for_return: int, client_id: int = 1) -> None:
        self.url = url
        self.mining = False
        self.maxtries = 10
        self.logger = setup_custom_logger(f"Hamster | User: {client_id}")
        self.token = None
        self.token_expiration = None
        self.max_days_for_return = max_days_for_return
        self.sleep_time = 0
        self.earn_passive_per_hour = 0
        self.earn_passive_per_seconds = 0

        if not self.auth_token(self.url):
            self.logger.error("Failed to get Auth Token. Stopping the class initialization.")
            return
        
        self.headers = {
            "accept": "/",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13; iPhone 15 Pro Max) AppleWebKit/533.2 (KHTML, like Gecko) Version/122.0 Mobile/15E148 Safari/533.2"
        }
        
        self.select_exchange()
        
        self.do_shits()
        
    def wait_time(self, max_taps: int, available_taps: int, taps_recover_per_sec: int):
        return round((max_taps - available_taps) / taps_recover_per_sec)

    def auth_token(self, url):
        if self.token and self.token_expiration and datetime.now() < self.token_expiration:
            self.logger.info("Using cached Auth Token.")
            return True

        payload = {
            "initDataRaw": urllib.parse.unquote(url).split('tgWebAppData=')[1].split('&tgWebAppVersion')[0],
            "fingerprint": finger_data
        }
        
        for _ in range(self.maxtries):
            try:
                response = requests.post(
                    'https://api.hamsterkombatgame.io/auth/auth-by-telegram-webapp',
                    json=payload
                ).json()
                self.token = response['authToken']
                self.token_expiration = datetime.now() + timedelta(minutes=30)
                self.logger.info("Auth Token fetched successfully.")
                return True
            except Exception as e:
                self.logger.warning(f"[!] Error in fetching Auth Token: {str(e)}. Retrying ")
                time.sleep(6)
        
        return False

    def post_request(self, endpoint, payload=None):
        if not self.token or (self.token_expiration and datetime.now() >= self.token_expiration):
            self.logger.info("Auth Token expired or invalid. Refreshing token...")
            if not self.auth_token(self.url):
                self.logger.error("Failed to refresh Auth Token. Stopping request.")
                return False
            self.headers["Authorization"] = f"Bearer {self.token}"

        for _ in range(self.maxtries):
            try:
                response = requests.post(
                    f'https://api.hamsterkombatgame.io{endpoint}',
                    json=payload,
                    headers=self.headers
                ).json()
                return response
            except Exception as e:
                self.logger.warning(f"[!] Error in {endpoint}: {str(e)}")
                time.sleep(3)
        return False

    def select_exchange(self, exchange_id: str = "bingx"):
        payload = {"exchangeId": exchange_id}
        return self.post_request('/clicker/select-exchange', payload)

    def list_tasks(self):
        return self.post_request('/clicker/list-tasks')

    def check_task(self, task_id: str = "streak_days"):
        payload = {"taskId": task_id}
        return self.post_request('/clicker/check-task', payload)

    
    def do_tasks(self):
        list_tasks = self.list_tasks()
        if not list_tasks or 'tasks' not in list_tasks:
            return
        for task in list_tasks['tasks']:
            if task['id'] == 'streak_days' and not task['isCompleted']:
                self.logger.debug('Doing daily tasks')
                self.check_task()
            
            elif task['id'] == 'streak_days_special' and not task['isCompleted']:
                self.logger.debug('Doing daily special tasks')
                self.check_task(task['id'])
    
    def do_youtube_tasks(self):
        tasks = self.list_tasks()
        for task in tasks.get('tasks', []):
            
            if task.get('id', None) and task.get('id').startswith('hamster_youtube_'):
                task_id = task.get('id')
                if task.get('isCompleted', False) == False:
                    self.check_task(task_id)
                    self.logger.debug(f'Checking Youtube Task: {task_id}')
            
            elif task['id'] == 'streak_days_special' and not task['isCompleted']:
                self.logger.debug('Doing daily special tasks')
                self.check_task(task['id'])
    
    def buy_skins(self, skin, timex=time.time() * 1000):
        payload = {"skinId": skin, "timestamp": int(timex)}
        return self.post_request('/clicker/buy-skin', payload)
    
    def get_skins(self):
        return self.post_request('/clicker/get-skin')
    
    def auto_buy_skins(self, max_skins=25):
        response_sync = self.info()
        all_skins     = self.get_skins()
        current_skins = []
        for skin in response_sync.get('skin', {}).get('available', []):
            current_skins.append(skin['skinId'])
        
        for skin in all_skins.get('skins', []):
            skin_id = skin['id']
            
            if skin['isAvailable'] and skin['isExpired'] == False:
                skin_number = int(skin_id.split('skin')[1])
                
                if skin_number <= max_skins and not skin_id in current_skins:
                    self.logger.debug(f'Buying Skin: {skin_id}')
                    self.buy_skins(skin_id)

    def claim_daily_combo(self):
        return self.post_request('/clicker/claim-daily-combo')
    
    def get_game_cipher(self, start_number: str):
        magic_index = int(start_number % (len(str(start_number)) - 2))
        res = ""
        for i in range(len(str(start_number))):
            res += '0' if i == magic_index else str(int(random.random() * 10))
        return res
    
    def minigame_cipher(self, uid, start_date, mini_game_id, sleep=40):
        secret1 = "R1cHard_AnA1"
        secret2 = "G1ve_Me_y0u7_Pa55w0rD"
        start_dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        start_number = int(start_dt.replace(tzinfo=timezone.utc).timestamp())
        cipher_score = (start_number + sleep) * 2
        combined_string = f'{secret1}{cipher_score}{secret2}'
        sig = hashlib.sha256(combined_string.encode()).digest()
        sig = base64.b64encode(sig).decode()
        game_cipher = self.get_game_cipher(start_number=start_number)
        data = f'{game_cipher}|{uid}|{mini_game_id}|{cipher_score}|{sig}'
        encoded_data = base64.b64encode(data.encode()).decode()
        return encoded_data

    def claim_daily_cipher(self, cipher: str):
        payload = {"cipher": cipher}
        response = self.post_request('/clicker/claim-daily-cipher', payload)
        if 'error_message' in response:
            return False, response['error_message']
        if 'dailyCipher' in response and response['dailyCipher']['isClaimed']:
            return True
        return response
    
    def cliam_minigame_keys(self, uid, start_date, score=0, sleep=40):
        r = self.post_request('/clicker/start-keys-minigame', payload={"miniGameId":"Candles"})
        time.sleep(random.randint(10, 20))
        payload = {
            'cipher': self.minigame_cipher(uid, start_date, 'Candles'),
            'miniGameId': 'Candles'
        }
        response_json = self.post_request('/clicker/claim-daily-keys-minigame', payload)
        profile_data = response_json.get('clickerUser') or response_json.get('found', {}).get('clickerUser', {})
        daily_mini_game = response_json.get('dailyKeysMiniGames') or response_json.get('found', {}).get(
            'dailyKeysMiniGames', {})
        bonus = int(response_json.get('bonus') or response_json.get('found', {}).get('bonus', 0))
        return profile_data, daily_mini_game, bonus
    
    def play_minigame_tiles(self, uid, start_date, score=0):    
        r = self.post_request('/clicker/start-keys-minigame', payload={"miniGameId":"Tiles"})
        time.sleep(random.randint(10, 20))
        payload = {
            'cipher': self.minigame_cipher(uid, start_date, 'Tiles', score),
            'miniGameId': 'Tiles'
        }
        response_json = self.post_request('/clicker/claim-daily-keys-minigame', payload)
        profile_data = response_json.get('clickerUser') or response_json.get('found', {}).get('clickerUser', {})
        daily_mini_game = response_json.get('dailyKeysMiniGames') or response_json.get('found', {}).get(
            'dailyKeysMiniGames', {})
        bonus = int(response_json.get('bonus') or response_json.get('found', {}).get('bonus', 0))
        return profile_data, daily_mini_game, bonus

    def buy_boost(self, boost_id: str, timex=time.time() * 1000):
        payload = {"boostId": boost_id, "timestamp": timex}
        return self.post_request('/clicker/buy-boost', payload)

    def buy_upgrade(self, upgrade_id: str, timex=time.time() * 1000):
        payload = {"upgradeId": upgrade_id, "timestamp": timex}
        return self.post_request('/clicker/buy-upgrade', payload)

    def buy_skins(self, skin, timex=time.time() * 1000):
        payload = {"skinId": skin, "timestamp": int(timex)}
        return self.post_request('/clicker/buy-skin', payload)
    
    def balance_coins(self):
        response = self.post_request('/clicker/sync')
        if response:
            self.earn_passive_per_hour = response['clickerUser']['earnPassivePerHour']
            self.earn_passive_per_seconds = response['clickerUser']['earnPassivePerSec']
            return response['clickerUser']['balanceCoins']
        return False

    def decode_cipher(self, cipher: str) -> str:
        encoded = cipher[:3] + cipher[4:]
        return base64.b64decode(encoded).decode('utf-8')
    
    def apply_promo(self, promo):
        payload = {"promoCode": promo}
        response = self.post_request('/clicker/apply-promo', payload)
        
        if response.get('error_code', False) == 'MaxKeysReceived':
            return False
        return True
    
    def info(self):
        response = self.post_request('/clicker/sync')
        if response:
            return response['clickerUser']
        return False
    
    def do_shits(self):
        uid = self.info()['id']
        response = self.post_request('/clicker/config')
        dailyCipher = response.get('dailyCipher', False)
        dailyKeysMiniGame = response.get('dailyKeysMiniGames', False)
        dailyKeysMiniGame_Candles = dailyKeysMiniGame.get('Candles', False)
        dailyKeysMiniGame_Tiles   = dailyKeysMiniGame.get('Tiles', False)
        promos = response.get('promos', False)
        
        if dailyCipher and dailyCipher.get('isClaimed', True) == False:
            cipher = self.decode_cipher(dailyCipher.get('cipher'))
            self.claim_daily_cipher(cipher)
        
        if dailyKeysMiniGame_Candles and dailyKeysMiniGame_Candles.get('isClaimed', True) == False:
            self.cliam_minigame_keys(uid, dailyKeysMiniGame_Candles.get('startDate'))
        
        if dailyKeysMiniGame_Tiles and dailyKeysMiniGame_Tiles.get('remainPoints', 0) > 0:
            remainPoints = dailyKeysMiniGame_Tiles.get('remainPoints', 0)
            points       = max(random.randint(int(remainPoints/2), remainPoints), random.randint(850, 1111))
            points       = min(remainPoints, points)
            points       = min(random.randint(150, 350), points)
            self.logger.debug(f"Playing Tiles | Points: {points} | Remain Points: {remainPoints}")
            x, y, bonus = self.play_minigame_tiles(uid, dailyKeysMiniGame_Tiles.get('startDate'), score=points)
            self.logger.debug(f"Playing Tiles | Bonus: {bonus} | Remain Points: {remainPoints - points}")
        
        self.do_youtube_tasks()
        self.auto_buy_skins()
        

    def tap(self, count: int, available_taps: int = 5500, timex=time.time() * 1000):
        payload = {"count": count, "availableTaps": available_taps, "timestamp": int(timex)}
        return self.post_request('/clicker/tap', payload)
    
    def check_boosts(self):
        response = self.post_request('/clicker/boosts-for-buy')
        if response:
            for boost in response['boostsForBuy']:
                if boost['id'] == 'BoostFullAvailableTaps' and boost['cooldownSeconds'] == 0 and boost['maxLevel'] - boost['level'] > 0:
                    self.buy_boost('BoostFullAvailableTaps')
                    return True
        return False

    def upgrade_item(self, upgrade_name: str):
        response = self.post_request('/clicker/upgrades-for-buy')
        if response:
            upgrades = response['upgradesForBuy']
            for upgrade_to_buy in upgrades:
                if upgrade_name.lower() in upgrade_to_buy['name'].lower():
                    upgrade_response = self.buy_upgrade(upgrade_to_buy['id'])
                    if 'error_code' in upgrade_response:
                        return False, upgrade_response['error_message']
                    try:
                        for item in upgrade_response['clickerUser']['upgrades']:
                            if item == upgrade_to_buy['id']:
                                return upgrade_response['clickerUser']['upgrades'][item]['level']
                    except KeyError:
                        continue
        return False
    
    def find_upgrade_level(self, upgrades, upgrade_id):
        for u in upgrades:
            if u['id'] == upgrade_id:
                if 'maxLevel' in u and u['isExpired']:
                    return u['level'], u['price']
                return u['level'] - 1, u['price']
        return False
    
    def find_best_upgrades(self, upgrades, time_horizon=2):
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
    
    def buy_bests(self):
        response = self.post_request('/clicker/upgrades-for-buy')
        if response:
            upgrades = response['upgradesForBuy']
            updates = []
            balance = self.balance_coins()
            for i in range(1, self.max_days_for_return + 1):
                sorted_upgrades = self.find_best_upgrades(upgrades, i)
                if len(sorted_upgrades) != 0:
                    break
            for upgrade_to_buy in sorted_upgrades:
                if 'cooldownSeconds' in upgrade_to_buy and upgrade_to_buy['cooldownSeconds'] > 0:
                    self.logger.debug('[~] Continue update for cool down:  ' + upgrade_to_buy['id'])
                    continue
            
                if upgrade_to_buy['condition'] and upgrade_to_buy['condition']['_type'] == 'ByUpgrade':
                    uid = upgrade_to_buy['condition']['upgradeId']
                    ulevel = upgrade_to_buy['condition']['level']
                    xlevel, xprice = self.find_upgrade_level(upgrades, uid)
                    if xlevel >= ulevel:
                        if balance < upgrade_to_buy['price']:
                            continue
                        self.logger.debug('[~] Updating: ' + upgrade_to_buy['id'] + ' | x_day_return: ' + str(upgrade_to_buy['x_day_return']))
                        response = self.buy_upgrade(upgrade_to_buy['id'])
                        if 'error_code' in response and response['error_code']:
                            continue
                        updates.append(upgrade_to_buy)
                        balance -= upgrade_to_buy['price']
                    elif xlevel < ulevel:
                        for i in range((ulevel - xlevel) + 1):
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
                    if 'error_code' in response and response['error_code']:
                        continue
                    updates.append(upgrade_to_buy)
                    balance -= upgrade_to_buy['price']
                    
            self.logger.debug(f'[~] Updated:  {len(updates)}')
            return updates


    def update_all(self):
        while len(self.buy_bests()) > 0:
            pass
        return
    
    def tap_all(self):
        taps = self.tap(1)
        if not taps:
            self.logger.error("Failed to get initial tap data.")
            return

        user_data = taps.get('clickerUser', {})
        max_taps = user_data.get('maxTaps', 0)
        available_taps = user_data.get('availableTaps', 0)
        earn_per_tap = user_data.get('earnPerTap', 0)
        taps_recover_per_sec = user_data.get('tapsRecoverPerSec', 0)

        self.sleep_time = self.wait_time(max_taps, available_taps, taps_recover_per_sec)
        if max_taps - available_taps > 50:
            self.logger.debug('[~] Wait for full charge')
            return

        total_taps = 0
        self.logger.info('Start clicking process on Hamster 🐹')

        while available_taps > 50:
            taps_to_perform = min(random.randint(1000, 2000), available_taps)
            total_taps += taps_to_perform

            taps = self.tap(taps_to_perform, available_taps)
            if not taps:
                self.logger.error("Failed to perform taps.")
                break

            user_data = taps.get('clickerUser', {})
            available_taps = user_data.get('availableTaps', 0)
            balance_coins = user_data.get('balanceCoins', 0)

            time.sleep(random.randint(1, 2))

        self.logger.info(f'Clicks were successful! | Total clicks: {total_taps} | Balance growth: (+{total_taps * earn_per_tap})')

        if self.check_boosts():
            return self.tap_all()

        return self.sleep_time + time.time() + (60 * random.randint(1, 6))

    def time_to_recharge(self):
        return self.sleep_time + (60 * random.randint(1, 6))
