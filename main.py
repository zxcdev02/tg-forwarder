import asyncio
import logging
import os
import threading

from flask import Flask

from forwarder import run_forwarder
from control_bot import run_control_bot
from state import state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    dot = "paused" if state.paused else "running"
    return f"tg-forwarder-bot: {dot} | forwarded={state.forwarded} filtered={state.filtered}"


@flask_app.route("/ping")
def ping():
    return "OK"


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)


async def main() -> None:
    await asyncio.gather(
        run_forwarder(),
        run_control_bot(),
    )


if __name__ == "__main__":
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    logger.info("🌐 Flask keep-alive запущено")
    asyncio.run(main())
