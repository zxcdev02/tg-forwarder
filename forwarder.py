import asyncio
import logging
import os

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaWebPage

from filters import MessageFilter
from state import state

logger = logging.getLogger("forwarder")

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

SOURCE_CHANNEL = int(os.environ.get("SOURCE_CHANNEL", "-1001875486764"))
TARGET_CHANNEL = int(os.environ.get("TARGET_CHANNEL", "-1002444819189"))
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "30"))

msg_filter = MessageFilter(os.path.join(os.path.dirname(__file__), "blacklist.json"))


async def run_forwarder() -> None:
    """Опитує SOURCE_CHANNEL і пересилає нові повідомлення в TARGET_CHANNEL.
    Поки state.paused == True — нічого не пересилає (тільки очікує)."""
    while True:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                logger.error("❌ Акаунт не авторизований! Перевір SESSION_STRING.")
                return

            me = await client.get_me()
            logger.info(f"✅ Авторизовано як: {me.first_name} (@{me.username})")

            messages = await client.get_messages(SOURCE_CHANNEL, limit=1)
            last_id = messages[0].id if messages else 0
            logger.info(f"📥 Починаємо з повідомлення ID: {last_id}")
            logger.info(f"🔄 Перевіряю канал кожні {CHECK_INTERVAL} секунд...")

            while True:
                try:
                    if state.paused:
                        # На паузі: не читаємо і не пересилаємо, тільки чекаємо.
                        await asyncio.sleep(2)
                        continue

                    if not client.is_connected():
                        logger.warning("⚠️ З'єднання втрачено, перепідключаємось...")
                        await client.connect()

                    messages = await client.get_messages(SOURCE_CHANNEL, min_id=last_id, limit=10)
                    for msg in reversed(messages):
                        if state.paused:
                            # Пауза настала посеред пачки — решту цієї пачки більше не чіпаємо.
                            break

                        text = msg.text or msg.message or ""

                        result = msg_filter.check(text)
                        if not result.passed:
                            logger.info(f"🚫 Пропущено ID {msg.id}: {result.reason}")
                            state.mark_filtered()
                            last_id = msg.id
                            continue

                        if msg.media and isinstance(msg.media, MessageMediaWebPage):
                            if text:
                                await client.send_message(TARGET_CHANNEL, text, link_preview=True)
                        elif msg.media:
                            await client.send_file(TARGET_CHANNEL, file=msg.media, caption=text)
                        elif text:
                            await client.send_message(TARGET_CHANNEL, text)

                        logger.info(f"✅ Переслано ID {msg.id}: {text[:60] if text else '[медіа]'}")
                        state.mark_forwarded(text or "[медіа]")
                        last_id = msg.id

                except Exception as e:
                    logger.error(f"❌ Помилка: {e}")
                    state.mark_error()
                    await asyncio.sleep(5)
                    try:
                        await client.connect()
                    except Exception:
                        break

                await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"❌ Критична помилка: {e}")
            state.mark_error()
        finally:
            await client.disconnect()

        logger.info("🔄 Перезапуск клієнта через 10 секунд...")
        await asyncio.sleep(10)
