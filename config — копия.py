import os
from dotenv import load_dotenv

load_dotenv()

# .env faylidan yoki Render Environment Variables'dan olinadi
BOT_TOKEN = os.getenv("BOT_TOKEN", "BU_YERGA_BOTFATHER_TOKENINI_QOYING")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DB_PATH = os.getenv("DB_PATH", "bot_database.db")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

DEFAULT_LANGUAGE = "uz"
MAX_VIDEO_HEIGHT = 720          # video yuklashda maksimal sifat
TELEGRAM_FILE_LIMIT_MB = 50     # oddiy Bot API orqali yuborish mumkin bo'lgan max hajm

PORT = int(os.getenv("PORT", "10000"))   # Render web-service porti
