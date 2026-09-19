# Telegram Channel Forwarder — Render.com + UptimeRobot

Копіює повідомлення з каналу-джерела у твій канал. Працює 24/7 безкоштовно через Flask keep-alive + UptimeRobot.

---

## 📋 Крок 1 — Отримати API_ID та API_HASH

1. Зайди на https://my.telegram.org
2. Логін → "API development tools"
3. Створи додаток (назва будь-яка)
4. Скопіюй `App api_id` і `App api_hash`

---

## 💻 Крок 2 — Отримати SESSION_STRING (на своєму ПК)

```bash
pip install telethon
python generate_session.py
```

Введи номер телефону у форматі +380XXXXXXXXX і код з Telegram.
Скопіюй SESSION_STRING — довгий рядок символів.

⚠️ Зберігай SESSION_STRING в секреті!

---

## 🐙 Крок 3 — Завантажити код на GitHub

1. Зареєструйся на https://github.com
2. Створи новий ПРИВАТНИЙ репозиторій
3. Завантаж всі файли (крім .env і *.session)

---

## 🚀 Крок 4 — Деплой на Render.com

1. Зайди на https://render.com → Sign up (через GitHub)
2. "New +" → "Web Service"
3. Підключи свій GitHub репозиторій
4. Налаштування:
   - Name: tg-forwarder
   - Environment: Python
   - Build Command: pip install -r requirements.txt
   - Start Command: python bot_hosted.py
5. Перейди в "Environment" і додай змінні:

| Змінна         | Значення              |
|----------------|-----------------------|
| API_ID         | твій api_id           |
| API_HASH       | твій api_hash         |
| SESSION_STRING | рядок з кроку 2       |
| SOURCE_CHANNEL | povitryanatrivogaaa   |
| TARGET_CHANNEL | radarofalarm          |

6. Натисни "Create Web Service"
7. Після деплою скопіюй URL сервісу (виглядає як https://tg-forwarder-xxxx.onrender.com)

---

## ⏰ Крок 5 — UptimeRobot (щоб бот не засипав)

1. Зайди на https://uptimerobot.com → Sign up (безкоштовно, без картки)
2. "Add New Monitor"
3. Налаштування:
   - Monitor Type: HTTP(s)
   - Friendly Name: TG Forwarder
   - URL: https://твій-url.onrender.com/ping
   - Monitoring Interval: Every 5 minutes
4. Натисни "Create Monitor"

Готово! UptimeRobot буде пінгувати твій бот кожні 5 хвилин — Render не засне ніколи.

---

## ✅ Перевірка

У логах Render ти побачиш:
```
🌐 Flask keep-alive сервер запущено
✅ Авторизовано як: Ім'я (@username)
📥 Джерело: Повітряна тривога
📤 Ціль: Radar of Alarm
👂 Слухаю нові повідомлення...
```
# tg-forwarder
