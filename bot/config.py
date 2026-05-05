import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not configured. Copy .env.example to .env and set BOT_TOKEN."
    )

BOT_USERNAME: str = os.getenv("BOT_USERNAME", "FancyFaceBot").strip()

ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in os.getenv("ADMIN_USER_IDS", "").split(",")
    if x.strip().isdigit()
]

CHANNEL_ID: int | str = os.getenv("CHANNEL_ID", "@avocado_photo_studio")
CHANNEL_URL: str = os.getenv("CHANNEL_URL", "https://t.me/avocado_photo_studio")

FAL_KEY: str = os.getenv("FAL_KEY", "").strip()
if not FAL_KEY:
    raise RuntimeError(
        "FAL_KEY is not configured. Copy .env.example to .env and set FAL_KEY."
    )

PAYMENT_PROVIDER_TOKEN: str = os.getenv("PAYMENT_PROVIDER_TOKEN", "").strip()
SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL", "").strip()
if not SUPABASE_DB_URL:
    raise RuntimeError(
        "SUPABASE_DB_URL is not configured. Copy .env.example to .env and set SUPABASE_DB_URL."
    )

WATERMARK_TEXT: str = f"@{BOT_USERNAME}"
FREE_CREDITS_FOR_SUBSCRIPTION: int = 2
REFERRAL_CREDITS: int = 2

PACKAGES: list[dict] = [
    {"id": "mini",     "credits": 5,   "price_rub": 139, "label": "5 фото — 139 ₽"},
    {"id": "basic",    "credits": 10,  "price_rub": 199, "label": "🔥 10 фото — 199 ₽ 🔥"},
    {"id": "standard", "credits": 50,  "price_rub": 499, "label": "50 фото — 499 ₽"},
    {"id": "premium",  "credits": 100, "price_rub": 899, "label": "💎 100 фото — 899 ₽ 💎"},
]
