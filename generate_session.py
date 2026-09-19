"""
Запусти цей скрипт ОДИН РАЗ локально на своєму ПК
щоб отримати SESSION_STRING для хостингу.

Інструкція:
1. pip install telethon
2. python generate_session.py
3. Введи свій номер телефону та код з Telegram
4. Скопіюй SESSION_STRING і встав у Railway
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = input("Введи API_ID: ").strip()
API_HASH = input("Введи API_HASH: ").strip()

async def main():
    async with TelegramClient(StringSession(), int(API_ID), API_HASH) as client:
        session_string = client.session.save()
        print("\n" + "="*60)
        print("✅ SESSION_STRING (скопіюй це):")
        print("="*60)
        print(session_string)
        print("="*60)
        print("\n⚠️  Зберігай цей рядок в секреті — це доступ до твого акаунту!")

asyncio.run(main())
