from telethon import TelegramClient, errors, functions
import psycopg2

from bot import conn


def invite_user_to_group():
    phone, api_id, api_hash = get_last_values_from_db()
    client = TelegramClient(phone, api_id, api_hash)

    try:
        # Входим в Telegram
        client.start()

        # Получаем Telegram ID пользователя из базы данных
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM memberss WHERE id = %s", (user_id,))
        telegram_id = cursor.fetchone()[0]

        # Приглашаем пользователя в группу
        result = client(functions.messages.ImportChatInviteRequest(invite_link))

        # Отправляем пользователю сообщение об успешном приглашении
        client.send_message(telegram_id, "Вы были приглашены в группу!")

    except errors.FloodWaitError as e:
        print(f"Ошибка: {str(e)}")
    finally:
        # Закрываем подключение к базе данных и завершаем сессию клиента
        cursor.close()
        conn.close()
        client.disconnect()