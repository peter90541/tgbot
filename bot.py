import asyncio
from aiogram import Bot, Dispatcher, types
import parser
from config import API_TOKEN
from database import create_db_conn
from spamer import invite_users_to_group

MAX_BUTTONS = 3
bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher(bot)
is_parser = {}
is_spam = {}
conn = create_db_conn()
global keyboard
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(text="Запускаю...", reply_markup=types.ReplyKeyboardRemove())
    is_parser[message.chat.id] = False
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
    await message.answer('Начинаю..', reply_markup=types.ReplyKeyboardRemove())
    await invite_users_to_group()


@dp.message_handler(lambda message: is_parser.get(message.chat.id, False))
async def parsed_link_handler(message: types.Message):
    try:
        await parser.parse_link_handler(message.text)
    except Exception as e:
        await message.answer("Ошибка:", {e})
    finally:
        await message.answer("Успешно!!", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Выберите действие:", reply_markup=keyboard)
        is_parser[message.chat.id] = False


if __name__ == '__main__':
    asyncio.run(dp.start_polling())
