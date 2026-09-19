import json
import re
import logging

logger = logging.getLogger(__name__)

class FilterResult:
    def __init__(self, passed: bool, reason: str = ""):
        self.passed = passed
        self.reason = reason

class MessageFilter:
    def __init__(self, blacklist_path: str):
        self.keywords = []
        self.patterns = []
        try:
            with open(blacklist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.keywords = [k.lower() for k in data.get("keywords", [])]
                self.patterns = [re.compile(p) for p in data.get("patterns", [])]
            logger.info(f"✅ Фільтр завантажено: {len(self.keywords)} ключових слів, {len(self.patterns)} патернів")
        except Exception as e:
            logger.error(f"❌ Помилка завантаження blacklist: {e}")

    def check(self, text: str) -> FilterResult:
        if not text:
            return FilterResult(passed=True)

        text_lower = text.lower()

        for keyword in self.keywords:
            if keyword in text_lower:
                return FilterResult(passed=False, reason=f"keyword: {keyword}")

        for pattern in self.patterns:
            if pattern.search(text):
                return FilterResult(passed=False, reason=f"pattern: {pattern.pattern}")

        return FilterResult(passed=True)
