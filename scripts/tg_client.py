import time, os, json

from telethon.sync import TelegramClient
from telethon.sync import functions
from telethon.tl.types import InputBotAppShortName

from scripts.cache_data import SimpleCache

with open('config.json') as f:
    data             = json.load(f)
    admin            = data['admin']
    api_id           = data['api_id']
    api_hash         = data['api_hash']
    cexio_ref_code   = data['cexio_ref_code']
    blum_ref_code    = data['blum_ref_code']

def getUrl(client: TelegramClient, peer: str, bot: str, url: str, platform: str = "ios", start_param: str = ""):
    return client(
        functions.messages.RequestWebViewRequest(
            peer=peer,
            bot=bot,
            platform=platform,
            url=url,
            from_bot_menu=False,
            start_param=start_param
        )
    )

def getAppUrl(client: TelegramClient, bot: str, platform: str = "ios", start_param: str = "", short_name: str = "start"):
    return client(
        functions.messages.RequestAppWebViewRequest(
            peer="me",
            app=InputBotAppShortName(bot_id=client.get_input_entity(bot), short_name=short_name),
            platform=platform,
            start_param=start_param
        )
    )


from telethon.sync import TelegramClient
import time

def create_client(api_id, api_hash, admin, cexio_ref_code):
    session_name = input("Please enter a unique name for the session (like: session_25 or you can enter phone number):  ")
    
    print(f"[INFO] Creating Telegram client for session: {session_name}")
    client = TelegramClient(
        f'sessions/{session_name}',
        api_id,
        api_hash,
        device_model=f"All-In-One(MA)"
    )

    print("[INFO] Starting Telegram client...")
    client.start()

    client_id = client.get_me(True).user_id
    print(f"[INFO] Client started. User ID: {client_id}")

    cache_db = SimpleCache(client_id)

    if not cache_db.exists('start_bots'):
        print("[INFO] Sending start messages to bots...")
        client.send_message('tapswap_bot', f'/start r_{admin}')
        time.sleep(6)
        client.send_message('hamster_kombat_bot', f'/start kentId{admin}')
        time.sleep(6)
        client.send_message('cexio_tap_bot', f'/start {cexio_ref_code}')
        time.sleep(6)
        client.send_message('BlumCryptoBot', f'/start ref_{blum_ref_code}')
        cache_db.set('start_bots', 4)
        print("[INFO] Start messages sent and cached.")

    if not cache_db.exists('tapswap_url'):
        print("[INFO] Fetching tapswap URL...")
        tapswap_url  = getUrl(
            client,
            'tapswap_bot',
            'tapswap_bot',
            'https://app.tapswap.ai/'
        ).url
        
        cache_db.set('tapswap_url', tapswap_url)
        print(f"[INFO] tapswap URL fetched and cached: {tapswap_url}")
        time.sleep(6)

    if not cache_db.exists('hamster_url'):
        print("[INFO] Fetching hamster URL...")
        hamster_url  = getAppUrl(
            client,
            'hamster_kombat_bot',
            start_param=f"kentId{admin}"
        ).url
        
        cache_db.set('hamster_url', hamster_url)
        print(f"[INFO] Hamster URL fetched and cached: {hamster_url}")
        time.sleep(6)

    if not cache_db.exists('cex_io_url'):
        print("[INFO] Fetching cex.io URL...")
        cex_io_url  = getUrl(
            client,
            'cexio_tap_bot',
            'cexio_tap_bot',
            'https://cexp.cex.io/'
        ).url
        
        cache_db.set('cex_io_url', cex_io_url)
        print(f"[INFO] cex.io URL fetched and cached: {cex_io_url}")
        time.sleep(6)
    
    if not cache_db.exists('blum_url'):
        print("[INFO] Fetching BlumCryptoBot URL...")
        blum_url  = getAppUrl(
            client,
            'BlumCryptoBot',
            start_param=f'ref_{blum_ref_code}',
        ).url
        
        cache_db.set('blum_url', blum_url)
        print(f"[INFO] BlumCryptoBot URL fetched and cached: {blum_url}")
        time.sleep(6)
    
    print("[INFO] Disconnecting Telegram client...")
    client.disconnect()
    
    print(f"\n\nSession {session_name} added and saved successfully! 🎉\n\n")
    print(f"[INFO] URLs fetched and cached:\n- tapswap URL: {tapswap_url}\n- hamster URL: {hamster_url}\n- cex.io URL: {cex_io_url}")



def check_session(session_name):
    client = TelegramClient(
        f'sessions/{session_name}',
        api_id,
        api_hash,
        device_model=f"All-In-One(MA)"
    )
    
    try:
        print(f"[INFO] Connecting to session: {session_name}")
        client.connect()
        
        if not client.is_user_authorized():
            print(f"[!] Bad Session: {session_name}")
            client.disconnect()
            return False
        
        client_id = client.get_me(True).user_id
        print(f"[INFO] Authorized session: {session_name}, User ID: {client_id}")

        cache_db = SimpleCache(client_id)
        
        if not cache_db.exists('start_bots'):
            print("[INFO] Starting bots for the first time.")
            client.send_message('tapswap_bot', f'/start r_{admin}')
            time.sleep(6)
            client.send_message('hamster_kombat_bot', f'/start kentId{admin}')
            time.sleep(6)
            client.send_message('cexio_tap_bot', f'/start {cexio_ref_code}')
            time.sleep(6)
            client.send_message('BlumCryptoBot', f'/start ref_{blum_ref_code}')
            cache_db.set('start_bots', 4)
        
        elif cache_db.get('start_bots') == 3:
            print("[INFO] Starting BlumCryptoBot.")
            client.send_message('BlumCryptoBot', f'/start ref_{blum_ref_code}')
            cache_db.set('start_bots', 4)
            
            if not cache_db.exists('blum_url'):
                print("[INFO] Fetching BlumCryptoBot URL...")
                blum_url  = getAppUrl(
                    client,
                    'BlumCryptoBot',
                    start_param=f'ref_{blum_ref_code}',
                    short_name='app'
                ).url
                
                cache_db.set('blum_url', blum_url)
                print(f"[INFO] BlumCryptoBot URL fetched and cached: {blum_url}")
                time.sleep(6)
        
        print(f"[INFO] Disconnecting session: {session_name}")
        client.disconnect()
    
    except Exception as e:
        print(f"[!] Error in session: {session_name}, {e}")

def reload_sessions():
    sessions = [f for f in os.listdir('sessions') if f.endswith('.session')]
    
    print("[INFO] Reloading sessions...")
    
    for session in sessions:
        print(f"[INFO] Checking session: {session}")
        check_session(session)
    
    print("[INFO] All sessions reloaded.")
