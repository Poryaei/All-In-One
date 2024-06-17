import asyncio
import json, os, time, aiocron, psutil, sys, subprocess, platform

from scripts.tapswap    import TapSwap
from scripts.hamster    import HamsterCombat
from scripts.cexio      import Cex_IO
from scripts.logger     import setup_custom_logger
from scripts.cache_data import SimpleCache
from scripts.tg_client  import create_client

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
    

if not os.path.exists('sessions'):
    os.mkdir('sessions')


m = """
Welcome to the Multi Session version of the All in One Clicker script! 🎉

GitHub Repository: https://github.com/Poryaei/All-In-One

Please choose:

1. Add account (session / clicker)
2. Run the bots
"""

print(m)

while input("Press 1 to add account (session / clicker), or any other key to start bots: ") == "1":
    create_client(api_id, api_hash, admin, cexio_ref_code)
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
    'start': False
}
clickers = {}
url_files = [f for f in os.listdir('cache') if f.endswith('.json')]


VERSION    = "1.1"
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
    tapswap = 0
    hamster = 0
    cexio   = 0
    hamster_earn_per_hour = 0
    data = ""
    
    for file in url_files:
        client_id = file.split('.json')[0]
        cache_db = SimpleCache(client_id)
        
        try:
            tapswap += float(cache_db.get('tapswap_balance'))
            data += f"User: `{client_id}` | 🟣 TapSwap: `{convert_big_number(float(cache_db.get('tapswap_balance')))}`\n"
        except:
            pass
        
        try:
            hamster += float(cache_db.get('hamster_balance'))
            hamster_earn_per_hour += float(cache_db.get('hamster_earn_per_hour'))
            data += f"User: `{client_id}` | 🐹 Hamster: `{convert_big_number(float(cache_db.get('hamster_balance')))}`\n"
            data += f"User: `{client_id}` | 🐹 Hamster PPH: `{convert_big_number(float(cache_db.get('hamster_earn_per_hour')))}`\n"
        except:
            pass
        
        try:
            cexio += float(cache_db.get('cex_io_balance'))
            data += f"User: `{client_id}` | ❣️Cex IO: `{convert_big_number(float(cache_db.get('cex_io_balance')))}`\n\n"
        except:
            pass
    
    return tapswap, hamster, cexio, hamster_earn_per_hour, data

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
        

async def answer(event):
    global db, db_steps
    
    text:str = event.raw_text
    user_id = event.sender_id
    
    if user_id < 1 or not user_id in [admin]:
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
        
    elif text == '/balance':
        m = await event.reply('Calculating the inventory. It might take some time ⏳.')
        tapswap, hamster, cexio, hamster_earn_per_hour, data = total_balance()
        await m.edit(f"""Total number of clickers: `{len(url_files)}`
Total inventories:

🤖 Total TapSwap: `{convert_big_number(tapswap)}`
🐹 Total Hamster: `{convert_big_number(hamster)}`
🔗 Total CEX IO:  `{convert_big_number(cexio)}`

🐹 Total Hamster Earn Per Hour:  `{convert_big_number(hamster_earn_per_hour)}`
🐹 Total Hamster Earn Per Day:   `{convert_big_number(hamster_earn_per_hour*24)}`
""")
    
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

🟢 `/click on` - Start collecting (Hamster ~ TapSwap ~ Cex IO)
🔴 `/click off` - Stop collecting (Hamster ~ TapSwap ~ Cex IO)

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


@aiocron.crontab('*/1 * * * *')
async def send_taps():
    global db
    if db['click'] != 'on' or db['start'] == True:
        return
    if platform.system() == "Windows":
        python_command = "python"
    else:
        python_command = "python3"

    if not os.path.exists('start.txt'):
        command = " ".join([python_command, "send_taps.py"])
        subprocess.Popen(command, shell=True)
        await client.send_message(admin, "Start Tapping ⛏️")
    
    

@aiocron.crontab('0 */12 * * *')
async def do_tasks():
    hamster_do_tasks()


@client.on(events.NewMessage())
async def handler(event):
    asyncio.create_task(
        answer(event)
    )


client.run_until_disconnected()
