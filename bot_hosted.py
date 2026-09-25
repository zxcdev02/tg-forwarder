import asyncio
import logging
import os
import threading
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaWebPage
from filters import MessageFilter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

SOURCE_CHANNEL = -1001875486764
TARGET_CHANNEL = -1002444819189
CHECK_INTERVAL = 30

msg_filter = MessageFilter("blacklist.json")

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

@flask_app.route("/ping")
def ping():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

async def main():
    while True:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                logger.error("❌ Акаунт не авторизований!")
                break

            me = await client.get_me()
            logger.info(f"✅ Авторизовано як: {me.first_name} (@{me.username})")

            messages = await client.get_messages(SOURCE_CHANNEL, limit=1)
            last_id = messages[0].id if messages else 0
            logger.info(f"📥 Починаємо з повідомлення ID: {last_id}")
            logger.info(f"🔄 Перевіряю канал кожні {CHECK_INTERVAL} секунд...")

            while True:
                try:
                    if not client.is_connected():
                        logger.warning("⚠️ З'єднання втрачено, перепідключаємось...")
                        await client.connect()

                    messages = await client.get_messages(SOURCE_CHANNEL, min_id=last_id, limit=10)
                    for msg in reversed(messages):
                        text = msg.text or msg.message or ""

                        # Перевірка фільтру
                        result = msg_filter.check(text)
                        if not result.passed:
                            logger.info(f"🚫 Пропущено ID {msg.id}: {result.reason}")
                            last_id = msg.id
                            continue

                        if msg.media and isinstance(msg.media, MessageMediaWebPage):
                            # Посилання з превʼю — надсилаємо як текст
                            if text:
                                await client.send_message(TARGET_CHANNEL, text, link_preview=True)
                        elif msg.media:
                            await client.send_file(TARGET_CHANNEL, file=msg.media, caption=text)
                        elif text:
                            await client.send_message(TARGET_CHANNEL, text)
                        logger.info(f"✅ Переслано ID {msg.id}: {text[:60] if text else '[медіа]'}")
                        last_id = msg.id

                except Exception as e:
                    logger.error(f"❌ Помилка: {e}")
                    await asyncio.sleep(5)
                    try:
                        await client.connect()
                    except:
                        break

                await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"❌ Критична помилка: {e}")
        finally:
            await client.disconnect()

        logger.info("🔄 Перезапуск через 10 секунд...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    logger.info("🌐 Flask запущено")
    asyncio.run(main())
