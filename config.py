import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")

DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
DB_NAME: str = os.getenv("DB_NAME", "translation_bot")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASS: str = os.getenv("DB_PASS", "")

# Канал для обязательной подписки
CHANNEL_URL: str = "https://t.me/petyapetuhh"
CHANNEL_ID: str = "@petyapetuhh"

# Админ
ADMIN_ID: int = 1174881844

# Текст подписки по умолчанию
DEFAULT_SUB_TEXT: str = (
    "📢 <b>Для использования бота необходимо подписаться на наш канал!</b>\n\n"
    "Подпишитесь и нажмите «Проверить подписку» 👇"
)

LANGUAGES: dict[str, str] = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
    "it": "🇮🇹 Italiano",
    "pt": "🇵🇹 Português",
    "uk": "🇺🇦 Українська",
    "pl": "🇵🇱 Polski",
    "tr": "🇹🇷 Türkçe",
    "ar": "🇸🇦 العربية",
    "zh-CN": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어",
    "hi": "🇮🇳 हिन्दी",
    "cs": "🇨🇿 Čeština",
    "nl": "🇳🇱 Nederlands",
    "sv": "🇸🇪 Svenska",
    "da": "🇩🇰 Dansk",
    "fi": "🇫🇮 Suomi",
    "no": "🇳🇴 Norsk",
    "ro": "🇷🇴 Română",
    "hu": "🇭🇺 Magyar",
    "el": "🇬🇷 Ελληνικά",
    "he": "🇮🇱 עברית",
    "th": "🇹🇭 ไทย",
    "vi": "🇻🇳 Tiếng Việt",
    "id": "🇮🇩 Bahasa Indonesia",
    "ms": "🇲🇾 Bahasa Melayu",
    "bg": "🇧🇬 Български",
}
