"""
Спільний стан між форвардером (Telethon) і керуючим ботом (aiogram).
Один процес, один event loop — тому звичайний клас без блокувань цілком безпечний.
"""

import time
from dataclasses import dataclass, field


@dataclass
class ForwarderState:
    paused: bool = False
    forwarded: int = 0
    filtered: int = 0
    errors: int = 0
    started_at: float = field(default_factory=time.time)
    last_message_at: float | None = None
    last_message_preview: str = ""

    def pause(self) -> bool:
        """True — якщо щойно поставили на паузу, False — якщо вже стояла."""
        if self.paused:
            return False
        self.paused = True
        return True

    def resume(self) -> bool:
        """True — якщо щойно зняли з паузи, False — якщо вже працював."""
        if not self.paused:
            return False
        self.paused = False
        return True

    def mark_forwarded(self, preview: str) -> None:
        self.forwarded += 1
        self.last_message_at = time.time()
        self.last_message_preview = preview[:80]

    def mark_filtered(self) -> None:
        self.filtered += 1

    def mark_error(self) -> None:
        self.errors += 1

    def uptime_str(self) -> str:
        s = int(time.time() - self.started_at)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        return f"{h}г {m}хв {sec}с"


state = ForwarderState()
