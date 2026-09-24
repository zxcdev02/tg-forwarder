import os
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from state import state

logger = logging.getLogger("control_bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Список Telegram ID, кому дозволено керувати ботом.
# Порожньо = дозволено всім (не рекомендується для продакшену).
ALLOWED_USERS: list[int] = [
    int(x) for x in os.environ.get("ALLOWED_USERS", "").split(",") if x.strip()
]

STOP_WORDS = {"стоп", "стоп!", "stop"}
START_WORDS = {"старт", "старт!", "start", "продовжити", "запустити"}

router = Router()


def allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


def main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardButton
    status_btn = (
        b(text="▶️ Запустити", callback_data="m:resume")
        if state.paused
        else b(text="⏹ Зупинити", callback_data="m:pause")
    )
    rows = [
        [status_btn, b(text="📊 Статус", callback_data="m:status")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def status_text() -> str:
    dot = "🔴 на паузі" if state.paused else "🟢 працює"
    last = (
        f"{state.last_message_preview}"
        if state.last_message_preview
        else "—"
    )
    return (
        "<b>📡 TG Forwarder</b>\n\n"
        f"Стан: {dot}\n"
        f"Переслано: {state.forwarded}\n"
        f"Відфільтровано: {state.filtered}\n"
        f"Помилок: {state.errors}\n"
        f"Останнє повідомлення: {last}\n"
        f"Аптайм: {state.uptime_str()}"
    )


@router.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    if not allowed(msg.from_user.id):
        await msg.answer("⛔️ Немає доступу.")
        return
    await msg.answer(status_text(), reply_markup=main_menu())


@router.message(Command("menu"))
async def cmd_menu(msg: Message) -> None:
    await cmd_start(msg)


@router.message(Command("status"))
async def cmd_status(msg: Message) -> None:
    if not allowed(msg.from_user.id):
        return
    await msg.answer(status_text(), reply_markup=main_menu())


@router.callback_query(F.data == "m:pause")
async def on_pause_btn(cb: CallbackQuery) -> None:
    if not allowed(cb.from_user.id):
        await cb.answer("⛔️ Немає доступу", show_alert=True)
        return
    state.pause()
    await cb.answer("⏹ Зупинено")
    await cb.message.edit_text(status_text(), reply_markup=main_menu())


@router.callback_query(F.data == "m:resume")
async def on_resume_btn(cb: CallbackQuery) -> None:
    if not allowed(cb.from_user.id):
        await cb.answer("⛔️ Немає доступу", show_alert=True)
        return
    state.resume()
    await cb.answer("▶️ Запущено")
    await cb.message.edit_text(status_text(), reply_markup=main_menu())


@router.callback_query(F.data == "m:status")
async def on_status_btn(cb: CallbackQuery) -> None:
    await cb.message.edit_text(status_text(), reply_markup=main_menu())
    await cb.answer()


@router.message(F.text.lower().in_(STOP_WORDS))
async def on_stop_word(msg: Message) -> None:
    """Просте слово 'стоп' від дозволеного користувача — пересилання ставиться на паузу."""
    if not allowed(msg.from_user.id):
        return
    just_paused = state.pause()
    text = "⏹ Зупинено. Бот більше нічого не пересилає, поки не напишеш «старт»." \
        if just_paused else "Уже на паузі."
    await msg.answer(text)


@router.message(F.text.lower().in_(START_WORDS))
async def on_start_word(msg: Message) -> None:
    if not allowed(msg.from_user.id):
        return
    just_resumed = state.resume()
    text = "▶️ Запущено. Пересилання відновлено." if just_resumed else "Уже працює."
    await msg.answer(text)


async def run_control_bot() -> None:
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    logger.info("🤖 Керуючий бот запущено")
    await dp.start_polling(bot)
