import asyncio
import json, os, time, aiocron, psutil, sys, subprocess, platform, datetime

from scripts.tapswap    import TapSwap
from scripts.hamster    import HamsterCombat
from scripts.cexio      import Cex_IO
from scripts.logger     import setup_custom_logger
from scripts.cache_data import SimpleCache
from scripts.tg_client  import create_client, reload_sessions, reload_rabbit_url

from telethon.sync import TelegramClient
from telethon import functions, types, events, Button, errors

from threading import Thread
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor




logger   = setup_custom_logger("mainapp")
executor = ThreadPoolExecutor(15)

with open('config.json') as f:
    data             = json.load(f)
    api_id           = data['api_id']
    api_hash         = data['api_hash']
    admin            = data['admin']
    bot_token        = data['bot_token']
    auto_upgrade     = data['auto_upgrade']
    max_tap_level    = data['max_tap_level']
    max_charge_level = data['max_charge_level']
    max_energy_level = data['max_energy_level']
    max_days_for_return = data['max_days_for_return']
    
    cexio_clicker    = data['cexio_clicker']
    tapswap_clicker  = data['tapswap_clicker']
    hamster_clicker  = data['hamster_clicker']
        
    cexio_ref_code   = data['cexio_ref_code']
    blum_ref_code    = data['blum_ref_code']
    

if not os.path.exists('sessions'):
    os.mkdir('sessions')


m = """
Welcome to the Multi Session version of the All in One Clicker script! 🎉

GitHub Repository: https://github.com/Poryaei/All-In-One

Please choose:

1. Add account (session / clicker)
2. Run the bots
3. Reload Sessions ( For New Bots )
"""

print(m)

while True:
    choice = input("Please enter your choice: ")
    
    if choice == "1":
        create_client(api_id, api_hash, admin, cexio_ref_code)
    elif choice == "2":
        break
    elif choice == "3":
        reload_sessions()
    else:
        print("Invalid choice. Please try again.")
    
    print(m)
    
if not os.path.exists('sessions'):
    os.mkdir('sessions')

client = TelegramClient('sessions/robot', api_id, api_hash)
client.start(bot_token=bot_token)

print("Client is ready")

if os.path.exists('start.txt'):
    os.unlink('start.txt')

db = {
    'click': 'on',
    'start': False,
    'rabbit_update': 0
}
clickers = {}
url_files = [f for f in os.listdir('cache') if f.endswith('.json')]
VERSION    = "1.2"
START_TIME = time.time()

def convert_time(uptime):
    hours   = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)

    return (hours if hours > 0 else 0), minutes

def hamster_do_tasks():
    def task(file):
        client_id = file.split('.json')[0]
        cache_db = SimpleCache(client_id)
        hamster_url = cache_db.get('hamster_url')
        try:
            hamster_client = HamsterCombat(hamster_url, max_days_for_return, client_id)
            hamster_client.do_tasks()
            return f"User: {client_id} | Tasks done"
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster Tasks: " + str(e))
            return f"User: {client_id} | Error: {str(e)}"
    
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        results = list(executor.map(task, url_files))
    return results

def daily_cipher(cipher: str):
    def task(file):
        client_id = file.split('.json')[0]
        cache_db = SimpleCache(client_id)
        hamster_url = cache_db.get('hamster_url')
        try:
            hamster_client = HamsterCombat(hamster_url, max_days_for_return, client_id)
            hamster_client.claim_daily_cipher(cipher)
            return f"User: {client_id} | Daily cipher claimed"
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster Daily Cipher: " + str(e))
            return f"User: {client_id} | Error: {str(e)}"
    
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        results = list(executor.map(task, url_files))
    return results

def daily_combo():
    def task(file):
        client_id = file.split('.json')[0]
        cache_db = SimpleCache(client_id)
        hamster_url = cache_db.get('hamster_url')
        try:
            hamster_client = HamsterCombat(hamster_url, max_days_for_return, client_id)
            hamster_client.claim_daily_combo()
            return f"User: {client_id} | Daily combo claimed"
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster Daily Combo: " + str(e))
            return f"User: {client_id} | Error: {str(e)}"
    
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        results = list(executor.map(task, url_files))
            
    return results

def buy_card(item: str):
    def task(file):
        client_id = file.split('.json')[0]
        cache_db = SimpleCache(client_id)
        hamster_url = cache_db.get('hamster_url')
        try:
            hamster_client = HamsterCombat(hamster_url, max_days_for_return, client_id)
            r = hamster_client.upgrade_item(item)
            return f"User: {client_id} | Card bought: {r}"
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster buy card: " + str(e))
            return f"User: {client_id} | Error: {str(e)}"
    
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        results = list(executor.map(task, url_files))
    return results



def total_balance():
    def safe_get_balance(cache_db, key, default=0.0):
        try:
            return float(cache_db.get(key))
        except (TypeError, ValueError):
            return default

    tapswap = 0
    hamster = 0
    cexio = 0
    blum = 0
    rabbit = 0
    hamster_earn_per_hour = 0

    for file in url_files:
        client_id = file.split('.json')[0]
        cache_db = SimpleCache(client_id)

        tapswap += safe_get_balance(cache_db, 'tapswap_balance')
        hamster += safe_get_balance(cache_db, 'hamster_balance')
        hamster_earn_per_hour += safe_get_balance(cache_db, 'hamster_earn_per_hour')
        cexio += safe_get_balance(cache_db, 'cex_io_balance')
        blum += safe_get_balance(cache_db, 'blum_balance')
        rabbit += safe_get_balance(cache_db, 'rabbit_balance')
        
    return tapswap, hamster, cexio, hamster_earn_per_hour, blum, rabbit

def account_balance(client_id):
    def safe_get_balance(cache_db, key, default=0.0):
        try:
            return float(cache_db.get(key))
        except (TypeError, ValueError):
            return default

    tapswap = 0
    hamster = 0
    cexio = 0
    blum = 0
    rabbit = 0
    hamster_earn_per_hour = 0


    cache_db = SimpleCache(client_id)

    tapswap += safe_get_balance(cache_db, 'tapswap_balance')
    hamster += safe_get_balance(cache_db, 'hamster_balance')
    hamster_earn_per_hour += safe_get_balance(cache_db, 'hamster_earn_per_hour')
    cexio += safe_get_balance(cache_db, 'cex_io_balance')
    blum += safe_get_balance(cache_db, 'blum_balance')
    rabbit += safe_get_balance(cache_db, 'rabbit_balance')
    account_data_json = cache_db.get('account_data')
    account_data = json.loads(account_data_json)
        
    return tapswap, hamster, cexio, hamster_earn_per_hour, blum, rabbit, account_data

def account_list():
    global url_files
    url_files = [f for f in os.listdir('cache') if f.endswith('.json')]
    accounts = []

    for file in url_files:
        try:
            client_id = file.split('.json')[0]
            cache_db = SimpleCache(client_id)
            
            account_data_json = cache_db.get('account_data')
            account_data = json.loads(account_data_json)
            first_name = account_data.get('first_name', 'Unknown')
            
            accounts.append(Button.inline(first_name, f'user_{client_id}'))
        except:
            continue

    grouped_buttons = [accounts[i:i + 3] for i in range(0, len(accounts), 3)]
    grouped_buttons.append([Button.inline('🔙', 'back')])
    return grouped_buttons


def convert_uptime(uptime):
    hours   = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)

    return (hours if hours > 0 else 0), minutes

def convert_big_number(num):
    suffixes = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion']

    if num == 0:
        return '0'

    num_abs   = abs(num)
    magnitude = 0

    while num_abs >= 1000:
        num_abs   /= 1000
        magnitude += 1

    formatted_num = '{:.2f}'.format(num_abs).rstrip('0').rstrip('.')

    return '{} {}'.format(formatted_num, suffixes[magnitude])

def get_server_usage():
    memory      = psutil.virtual_memory()
    mem_usage   = memory.used / 1e6
    mem_total   = memory.total / 1e6
    mem_percent = memory.percent
    cpu_percent = psutil.cpu_percent()
    
    return {
        'memory_usage_MB': mem_usage,
        'memory_total_MB': mem_total,
        'memory_percent': mem_percent,
        'cpu_percent': cpu_percent
    }

def split_string_by_length(input_string, chunk_length):
    return [input_string[i:i + chunk_length] for i in range(0, len(input_string), chunk_length)]
        
def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

async def answer(event):
    global db, db_steps
    
    text:str = event.raw_text
    user_id = event.sender_id
    
    if user_id and user_id < 1 or not user_id in [admin]:
        return
    
    if text == '/start':
        await event.reply('👋 Welcome to the Clickers Management Bot! 🤖\n\nTo view the menu, send the command /help. 😉')
    
    elif text == '/ping':
        await event.reply('I am online! 🌐')
    
    elif text == '/claim_daily_combo':
        m = await event.reply('It might take some time ⏳.')
        daily_combo()
        await m.edit('🚀 Your request has been sent.')
    
    elif text.startswith('/cipher '):
        cipher = text.split('/cipher ')[1]
        m = await event.reply('It might take some time ⏳.')
        daily_cipher(cipher)
        await m.edit('🚀 Your request has been sent.')
    
    elif text.startswith('/click '):
        stats = text.split('/click ')[1]
        if not stats in ['off', 'on']:
            await event.reply('❌ Bad Command!')
            return
        
        db['click'] = stats
        if stats == 'on':
            await event.reply('✅ Mining Started!')
        else:
            await event.reply('💤 Mining turned off!')
    
    elif text.startswith('/buy '):
        item = text.split('/buy ')[1]
        m = await event.reply('It might take some time ⏳.')
        buy_card(item)
        await m.edit('🚀 Your request has been sent.')
    
    elif text == '/accounts':
        await event.reply('🍑 Accounts list:\n\n', buttons=account_list())
        
    elif text == '/balance':
        m = await event.reply('Calculating the inventory. It might take some time ⏳.')
        tapswap, hamster, cexio, hamster_earn_per_hour, blum, rabbit = total_balance()
        btn = [
            [Button.inline('🤖 TapSwap 🤖', 'tapswap'), Button.inline(f'{convert_big_number(tapswap)}', 'tapswap')],
            [Button.inline('🐹 Hamster 🐹', 'hamster'), Button.inline(f'{convert_big_number(hamster)}', 'hamster')],
            [Button.inline('🔗 Cex  IO 🔗', 'cexio'), Button.inline(f'{convert_big_number(cexio)}', 'cexio')],
            [Button.inline('⚫️ Blum ⚫️', 'blum'), Button.inline(f'{convert_big_number(blum)}', 'blum')],
            [Button.inline('🐰 Rabbit 🐰', 'rabbit'), Button.inline(f'{convert_big_number(rabbit)}', 'rabbit')],
            [Button.inline('📊 Accounts 📊', 'back_accountlist')],
        ]
        await m.edit(f"""**Total number of clickers**: `{len(url_files)}`

🐹 **Total Hamster Earn Per Hour** :  `{convert_big_number(hamster_earn_per_hour)}`
🐹 **Total Hamster Earn Per Day**    :   `{convert_big_number(hamster_earn_per_hour*24)}`
""", buttons=btn)
    
    elif text == '/help':
        su = get_server_usage()

        mem_usage   = su['memory_usage_MB']
        mem_total   = su['memory_total_MB']
        mem_percent = su['memory_percent']
        cpu_percent = su['cpu_percent']
        
        _uptime            = time.time() - START_TIME
        _hours, _minutes   = convert_uptime(_uptime)
        _clicker_stats     = "ON 🟢" if db['click'] == 'on' else "OFF 🔴"

        await event.reply(f"""
🤖 Welcome to All-In-One (MA) Collector Bot!
Just a powerful clicker and non-stop bread 🚀


💻 Author: `Abolfazl Poryaei`
📊 Clicker stats: `{_clicker_stats}`
⏳ Uptime: `{_hours} hours and {_minutes} minutes`
🎛 CPU usage: `{cpu_percent:.2f}%`
🎚 Memory usage: `{mem_usage:.2f}/{mem_total:.2f} MB ({mem_percent:.2f}%)`

🤖 Global commands:

📊 `/accounts` - Accounts List

🟢 `/click on` - Start collecting
🔴 `/click off` - Stop collecting

🟡 `/ping` - Check if the robot is online
🟢 `/help` - Display help menu
⚪️ `/balance` - Show Total balance
⚫️ `/stop` - Stop the robot




🐹 Special Hamster Commands:

🟠 `/buy item` - Purchase an item/card ( `/buy Fan tokens` )
🟠 `/claim_daily_combo` - Claim daily combo ( `You need to purchase items by commands` )
🟠 `/cipher CIPHER` - Claim daily cipher ( `/cipher BTC` )



Coded By: @uPaSKaL | GitHub: [Poryaei](https://github.com/Poryaei)

                          """)
        

    elif text == '/version':
        await event.reply(f"ℹ️ Version: {VERSION}\n\nCoded By: @uPaSKaL | GitHub: [Poryaei](https://github.com/Poryaei)")
    
    elif text == '/stop':
        await event.reply('👋')
        sys.exit()

async def callback(event):
    data:str = event.data.decode()
    user_id = event.sender_id
    
    if user_id and user_id < 1 or not user_id in [admin]:
        return
    
    if data == 'back':
        await event.delete()
        await client.send_message(int(user_id), "👋 Welcome to the Clickers Management Bot! 🤖\n\nTo view the menu, send the command /help. 😉")
    
    elif data == 'back_accountlist':
        await event.edit('🍑 Accounts list:\n\n', buttons=account_list())
    
    elif data.startswith('user_'):
        client_id = data.split('user_')[1]
        tapswap, hamster, cexio, hamster_earn_per_hour, blum, rabbit, account_data = account_balance(client_id)
        btn = [
            [Button.inline('back', b'back_accountlist')]
        ]
        await event.edit(f"""
👤 **Account**:
🌟 `Name`              : **{account_data['first_name']}**
❤️ `UserId`         : `{account_data['id']}`
👥 `Username`    : @{account_data['username']}
📞 `Phone`           : +{account_data['phone']}

🐹 **Hamster**:
💰 `Balance`     : `{convert_big_number(hamster)}`
📈 `PPH`              : `{convert_big_number(hamster_earn_per_hour)}`

🔗 **Cex IO**:
💰 `Balance`     : `{convert_big_number(cexio)}`

⚫️ **Blum**:
💰 `Balance`     : `{convert_big_number(blum)}`

🐰 **Rabbit**:
💰 `Balance`     : `{convert_big_number(rabbit)}`
""", buttons=btn)
        
    


@aiocron.crontab('*/1 * * * *')
async def send_taps():
    global db
    if db['click'] != 'on' or db['start'] == True:
        return
    if platform.system() == "Windows":
        python_command = "python"
    else:
        python_command = "python3"
    
    if time.time() - db['rabbit_update'] > 60*60*2:
        try:
            command = " ".join([python_command, "update_url.py"])
            subprocess.Popen(command, shell=True)
            reload_rabbit_url()
            db['rabbit_update'] = time.time()
        except Exception as e:
            await client.send_message(admin, str(e))

    if not os.path.exists('start.txt'):
        command = " ".join([python_command, "send_taps.py"])
        subprocess.Popen(command, shell=True)




@aiocron.crontab('0 */12 * * *')
async def do_tasks():
    hamster_do_tasks()
    


@client.on(events.NewMessage())
async def handler(event):
    asyncio.create_task(
        answer(event)
    )

@client.on(events.CallbackQuery())
async def handler(event):
    asyncio.create_task(
        callback(event)
    )


client.run_until_disconnected()
