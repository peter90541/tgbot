import asyncio
import psycopg2
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from aiogram import Bot, Dispatcher, types

API_TOKEN = "6253410351:AAH-pHyLhDYLSxwK4553jYuWKSNE82Gyrwc"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
is_parser = {}

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="9054"
)


def get_last_values_from_db(connc, table_name, column_names):
    try:
        cur = connc.cursor()
        query = f"SELECT {', '.join(column_names)} FROM {table_name} ORDER BY id DESC LIMIT 1"
        cur.execute(query)
        row = cur.fetchone()
        cur.close()
        return tuple(row)
    except Exception as e:
        print(e)
        return None


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
        is_parser[message.chat.id] = False
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('Парсер'))
        keyboard.add(types.KeyboardButton('Инвайтер'))
        keyboard.add(types.KeyboardButton('Спамер'))
        await message.answer('Выберите действие:', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Парсер')
async def parser_handler(message: types.Message):
    is_parser[message.chat.id] = True
    await message.answer('Введите ссылку на чат:', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == 'Инвайтер')
async def inviter_handler(message: types.Message):
    await message.answer('Вы выбрали действие "Инвайтер"!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == 'Спамер')
async def spammer_handler(message: types.Message):
    await message.answer('Вы выбрали действие "Спамер"!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: is_parser.get(message.chat.id, False))
async def parse_link_handler(message: types.Message):
    chat_link = message.text
    if chat_link.startswith('https://t.me/'):
        try:
            await message.answer('Начинаю парсинг...')
            column_names = ["api_id", "api_hash", "phone"]
            api_id, api_hash, phone = get_last_values_from_db(conn, 'accounts', column_names)
            cursor = conn.cursor()
            client = TelegramClient(phone, api_id, api_hash)
            await client.start()
            result = await client(ImportChatInviteRequest(chat_link))

            if chat_link.startswith('https://t.me/'):
                target_group_entity = await client.get_entity(chat_link)
                target_group = target_group_entity.id

                print('Joining the group...')
                await client(JoinChannelRequest(chat_link))
                print('Joined the group.')

                print('Searching...')
                all_participants = client.get_participants(target_group, aggressive=True)
                for user in all_participants:
                    if user.id:
                        cursor.execute("SELECT COUNT(*) FROM members WHERE user_id=%s", (user.id,))
                        if cursor.fetchone()[0] == 0:
                            if user.username:
                                username = user.username
                            else:
                                username = "-"
                            if user.first_name:
                                first_name = user.first_name
                            else:
                                first_name = "-"
                            if user.last_name:
                                last_name = user.last_name
                            else:
                                last_name = "-"
                            cursor.execute("INSERT INTO members (user_id, first_name, last_name) VALUES (%s, %s, %s)",
                                           (user.id, first_name, last_name))
                            conn.commit()
                print('Parsing group members completed successfully.')
            input('Press Enter to exit...')
            client.disconnect()
            cursor.close()
            conn.close()
        except Exception as e:
            await message.answer(f'Произошла ошибка: {e}', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Неверная ссылка', reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    asyncio.run(dp.start_polling())
