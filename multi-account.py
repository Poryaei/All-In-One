import asyncio
import json, os, time, aiocron, psutil, sys

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
executor = ThreadPoolExecutor(5)



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

    


client = TelegramClient('sessions/robot', api_id, api_hash)
client.start(bot_token=bot_token)

db = {
    'click': 'on'
}
clickers = {}


VERSION    = "1.0.0"
START_TIME = time.time()


def create_clickers():
    global clickers
    
    logger.info('Start connecting the clickers! 💻🔗')
    url_files = [f for f in os.listdir('cache') if f.endswith('.json')]
    tasks = []
    
    def connect(file):
        try:
            client_id = file.split('.json')[0]
            cache_db = SimpleCache(client_id)
            
            tapswap_url = cache_db.get('tapswap_url')
            hamster_url = cache_db.get('hamster_url')
            cex_io_url  = cache_db.get('cex_io_url')

            tapswap_client = TapSwap(tapswap_url, auto_upgrade, max_charge_level, max_energy_level, max_tap_level, client_id)
            hamster_client = HamsterCombat(hamster_url, max_days_for_return, client_id)
            cex_io_client  = Cex_IO(cex_io_url, client_id)    
            
            clickers[client_id] = {
                'tapswap' : tapswap_client,
                'hamster' : hamster_client,
                'cexio'   : cex_io_client,
                'next_tap': 0
            }
        except Exception as e:
            logger.error(f'Error in building client[{file}]: ' + str(e))
    
    for file in url_files:
        tasks.append(executor.submit(connect, file))
        
    for t in tasks:
        t.result()
    
    logger.info(f'{len(clickers)} clients have been successfully prepared.')
    return clickers


def start_clickers():
    global clickers
    
    tasks = []
    def click(clicker, client_id):
        tapswap_client = clicker['tapswap']
        hamster_client = clicker['hamster']
        cex_io_client  = clicker['cexio']
        next_tap       = clicker['next_tap']
        
        if tapswap_clicker == "on":
            
            if time.time() > next_tap:
                try:
                    Thread(target=tapswap_client.click_all).start()
                    time_to_recharge = tapswap_client.time_to_recharge()
                    clickers[client_id]['next_tap'] = time.time()+time_to_recharge
                    logger.info(f"User: {client_id} | Sleeping: {time_to_recharge} seconds ...")
                except Exception as e:
                    time_to_recharge = 0
                    logger.warning(f"User: {client_id} | Error in click all: " + str(e))
        
        if cexio_clicker == "on":
            try:
                if cex_io_client.farms_end_time() < 1:
                    cex_io_client.check_for_clicks()
            except Exception as e:        
                logger.warning(f"User: {client_id} | Error in Cex_IO Click: " + str(e))
        
        if hamster_clicker == "on":
            try:
                if time.time() > hamster_client.sleep_time:
                    Thread(target=hamster_client.tap_all).start()
                Thread(target=hamster_client.update_all).start()
            except Exception as e:        
                logger.warning(f"User: {client_id} | Error in Hamster Click: " + str(e))
    
    for client_id, clicker in clickers.items():
        tasks.append(executor.submit(click, clicker, client_id))
    
    for t in tasks:
        t.result()

def hamster_do_tasks():
    global clickers
    
    for client_id, clicker in clickers.items():
        
        hamster_client = clicker['hamster']
        try:
            hamster_client.do_tasks()
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster Tasks: " + str(e))

def daily_cipher(cipher:str):
    global clickers
    
    for client_id, clicker in clickers.items():
                
        hamster_client = clicker['hamster']
        try:
            hamster_client.claim_daily_cipher(cipher)
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster Daily Cipher: " + str(e))

def daily_combo():
    global clickers
    
    for client_id, clicker in clickers.items():
                
        hamster_client = clicker['hamster']
        try:
            hamster_client.claim_daily_combo()
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster Daily Combo: " + str(e))

def buy_card(item:str):
    global clickers
    
    for client_id, clicker in clickers.items():
                
        hamster_client = clicker['hamster']
        try:
            hamster_client.upgrade_item(item)
        except Exception as e:
            logger.warning(f"User: {client_id} | Error in Hamster buy card: " + str(e))


def retrieve_tapswap(client_id, tapswap_client):
    try:
        return float(tapswap_client.shares())
    except Exception as e:
        logger.error(f'User: {client_id} | Error in retrieving balance in TapSwap: ' + str(e))
        return 0

def retrieve_hamster(client_id, hamster_client):
    try:
        balance = float(hamster_client.balance_coins())
        earn_per_hour = float(hamster_client.earn_passive_per_hour)
        return balance, earn_per_hour
    except Exception as e:
        logger.error(f'User: {client_id} | Error in retrieving balance in Hamster: ' + str(e))
        return 0, 0

def retrieve_cexio(client_id, cex_io_client):
    try:
        return float(cex_io_client.balance())
    except Exception as e:
        logger.error(f'User: {client_id} | Error in retrieving balance in CEX.IO: ' + str(e))
        return 0

def total_balance():
    global clickers
    
    tapswap = 0
    hamster = 0
    cexio   = 0
    hamster_earn_per_hour = 0
    
    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        futures = []
        
        for client_id, clicker in clickers.items():
            tapswap_client = clicker['tapswap']
            hamster_client = clicker['hamster']
            cex_io_client  = clicker['cexio']
            
            futures.append(executor.submit(retrieve_tapswap, client_id, tapswap_client))
            futures.append(executor.submit(retrieve_hamster, client_id, hamster_client))
            futures.append(executor.submit(retrieve_cexio, client_id, cex_io_client))
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if isinstance(result, tuple):
                hamster += result[0]
                hamster_earn_per_hour += result[1]
            else:
                if futures.index(future) % 3 == 0:
                    tapswap += result
                else:
                    cexio += result
    
    return tapswap, hamster, cexio, hamster_earn_per_hour

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
        tapswap, hamster, cexio, hamster_earn_per_hour = total_balance()
        await m.edit(f"""Total number of clickers: `{len(clickers)}`
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
    
    




create_clickers()
start_clickers()

@aiocron.crontab('*/5 * * * *')
async def send_taps():
    if db['click'] != 'on':
        return
    start_clickers()

@aiocron.crontab('0 */12 * * *')
async def do_tasks():
    hamster_do_tasks()


@client.on(events.NewMessage())
async def handler(event):
    asyncio.create_task(
        answer(event)
    )


client.run_until_disconnected()
