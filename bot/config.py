import os
from pathlib import Path
from dotenv import load_dotenv

# Loyiha ildiz papkasidagi .env ni yuklash
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID larini olish (vergul bilan ajratilgan raqamlar)
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS = set()
if ADMIN_IDS_RAW:
    for aid in ADMIN_IDS_RAW.split(","):
        aid = aid.strip()
        if aid.isdigit():
            ADMIN_IDS.add(int(aid))

# Ma'lumotlar bazasi yo'li
DB_PATH_RAW = os.getenv("DATABASE_PATH", "data/bot.db")
DATABASE_PATH = BASE_DIR / DB_PATH_RAW
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Qidiruv sozlamalari
ENABLE_ONLINE_SEARCH = os.getenv("ENABLE_ONLINE_SEARCH", "true").lower() in ("true", "1", "yes")
SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "5"))
SEARCH_CACHE_DAYS = int(os.getenv("SEARCH_CACHE_DAYS", "14"))
