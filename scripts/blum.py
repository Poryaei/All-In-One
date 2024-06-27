import requests
import urllib
import time
import random
import sys

from scripts.logger import setup_custom_logger


class Blum:
    def __init__(self, url, client_id, referralToken: str = ""):
        self.url = url
        self.mining = True
        self.session = requests.Session()
        self.authData = self.extract_auth_data(url)
        self.logger = setup_custom_logger(f"Blum | User: {client_id}")
        self.referralToken = referralToken
        self.update_token_time = 0
        self.session.headers = self.default_headers()
        self.active = True
        self.provider_telegram_mini_app()
        if self.active:
            self.session.headers['Authorization'] = f"Bearer {self.token}"

    def extract_auth_data(self, url: str) -> str:
        return urllib.parse.unquote(url).split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]

    def default_headers(self) -> dict:
        return {
            "accept": "/",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "Priority": "u=1, i",
            "Reffer": "https://telegram.blum.codes/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

    def provider_telegram_mini_app(self):
        if not self.active:
            return
        if time.time() - self.update_token_time < 30 * 60:
            return

        data = {'query': self.authData}
        if self.referralToken:
            data['referralToken'] = self.referralToken

        response = self.make_request('POST', 'https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP', json=data)
        if response and 'username' in response:
            self.logger.error('[!] Please enter the Blum bot once and choose your username. Then restart the script.')
            self.active = False
            return

        if response:
            self.token = response['token']['access']
            self.user_id = response['token']['user']['id']['id']
            self.user_username = response['token']['user']['username']
            self.update_token_time = time.time()
            return response
    
    def me(self) -> dict:
        if not self.active:
            return {}
        return self.make_request('GET', 'https://gateway.blum.codes/v1/user/me')
    
    def claim_pass(self) -> dict:
        if not self.active:
            return {}
        r = self.make_request('GET', 'https://game-domain.blum.codes/api/v1/daily-reward?offset=-210')
        return self.make_request('POST', 'https://game-domain.blum.codes/api/v1/daily-reward?offset=-210'), r

    def time(self) -> dict:
        if not self.active:
            return {}
        return self.make_request('GET', 'https://game-domain.blum.codes/api/v1/time/now')

    def balance(self) -> dict:
        if not self.active:
            return {}
        self.provider_telegram_mini_app()
        return self.make_request('GET', 'https://game-domain.blum.codes/api/v1/user/balance')

    def start_farm(self) -> dict:
        if not self.active:
            return {}
        return self.make_request('POST', 'https://game-domain.blum.codes/api/v1/farming/start')

    def claim_farm(self) -> dict:
        if not self.active:
            return {}
        return self.make_request('POST', 'https://game-domain.blum.codes/api/v1/farming/claim')

    def play_and_claim(self):
        if not self.active:
            return {}
        game_response = self.make_request('POST', 'https://game-domain.blum.codes/api/v1/game/play')

        if game_response:
            game_id = game_response['gameId']
            self.time()
            time.sleep(random.randint(30, 36))
            claim_data = {"gameId": game_id, "points": random.randint(200, 220)}
            return self.make_request('POST', 'https://game-domain.blum.codes/api/v1/game/claim', json=claim_data)

    def check_claim_and_play(self):
        if not self.active:
            return {}
        balance = self.balance()

        if balance:
            if 'farming' in balance:
                if int(time.time() * 1000) > balance['farming']['endTime']:
                    self.claim_farm()
                    self.start_farm()
            else:
                self.start_farm()

            for _ in range(balance.get('playPasses', 0)):
                self.logger.debug('[+] Playing Game')
                self.play_and_claim()

    def make_request(self, method: str, url: str, **kwargs) -> dict:
        if not self.active:
            return {}
        try:
            response = self.session.request(method, url, **kwargs)
            if response.text == "OK":
                return response
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to {url} failed: {e} | {response.text}")
            return {}
