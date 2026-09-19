import asyncio
import logging
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфіг з .env
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SOURCE_CHANNEL = os.environ.get("SOURCE_CHANNEL", "povitryanatrivogaaa")
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL", "radarofalarm")

client = TelegramClient("session", API_ID, API_HASH)


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        msg = event.message
        text = msg.text or msg.message or ""

        # Якщо є медіа (фото, відео, документ)
        if msg.media:
            if isinstance(msg.media, MessageMediaPhoto):
                await client.send_file(
                    TARGET_CHANNEL,
                    file=msg.media,
                    caption=text
                )
            elif isinstance(msg.media, MessageMediaDocument):
                await client.send_file(
                    TARGET_CHANNEL,
                    file=msg.media,
                    caption=text
                )
            else:
                # Інші типи медіа — просто пересилаємо файл
                await client.send_file(
                    TARGET_CHANNEL,
                    file=msg.media,
                    caption=text
                )
        elif text:
            # Тільки текст
            await client.send_message(TARGET_CHANNEL, text)

        logger.info(f"✅ Переслано повідомлення: {text[:60]}...")

    except Exception as e:
        logger.error(f"❌ Помилка при пересиланні: {e}")


async def main():
    logger.info("🚀 Запуск userbot...")
    await client.start()

    me = await client.get_me()
    logger.info(f"✅ Авторизовано як: {me.first_name} (@{me.username})")

    source = await client.get_entity(SOURCE_CHANNEL)
    target = await client.get_entity(TARGET_CHANNEL)
    logger.info(f"📥 Джерело: {source.title}")
    logger.info(f"📤 Ціль: {target.title}")

    logger.info("👂 Слухаю нові повідомлення...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
