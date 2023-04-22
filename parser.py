import types
from urllib.parse import urlparse

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendMessageRequest
from bot import conn
from config import column_names
from database import get_last_values_from_db


async def parse_link_handler(message):
    chat_link = message
    if chat_link.startswith('https://t.me/'):
        try:
            api_id, api_hash, phone = get_last_values_from_db(conn, 'accounts', column_names)
            cursor = conn.cursor()
            client = TelegramClient(phone, api_id, api_hash)
            await client.start()
            path = urlparse(message).path
            channel_name = path.rsplit('/', 1)[-1]
            await client(JoinChannelRequest(channel_name))
            if chat_link.startswith('https://t.me/'):
                target_group_entity = await client.get_entity(chat_link)
                target_group = target_group_entity.id
                access_hash = target_group_entity.access_hash
                all_participants = await client.get_participants(target_group, aggressive=True)
                for user in all_participants:
                    if user.id:
                        cursor.execute("SELECT COUNT(*) FROM memberss WHERE user_id=%s", (user.id,))
                        if cursor.fetchone()[0] == 0:
                            if user.first_name:
                                first_name = user.first_name
                            else:
                                first_name = "-"
                            if user.last_name:
                                last_name = user.last_name
                            else:
                                last_name = "-"
                            cursor.execute("INSERT INTO memberss (user_id, first_name, last_name, access_hash) VALUES (%s, %s, %s, %s)",
                                           (user.id, first_name, last_name, access_hash))
                            conn.commit()
            client.disconnect()
            cursor.close()
        except Exception as e:
            print(e)