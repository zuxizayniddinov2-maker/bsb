import aiosqlite
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from bot.config import DATABASE_PATH

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db():
    """Async SQLite ulanish kontekst menejeri (row_factory bilan)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON;")
        yield db


async def init_db():
    """Jadvallarni yaratish va dastlabki sozlash."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Sinflar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)

        # 2. Choraklar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS terms (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)

        # 3. Fanlar jadvali (har bir sinf uchun alohida)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                icon TEXT DEFAULT '📖',
                order_num INTEGER DEFAULT 0,
                FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
                UNIQUE (grade_id, code)
            );
        """)

        # 4. Baholash turlari (BSB, CHSB)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS assessment_types (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            );
        """)

        # 5. Topshiriqlar va javoblar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade_id INTEGER NOT NULL,
                term_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                type_code TEXT NOT NULL,
                assignment_num INTEGER NOT NULL,
                title TEXT NOT NULL,
                questions_text TEXT,
                answers_text TEXT,
                source_url TEXT,
                source_name TEXT,
                file_id TEXT,
                file_type TEXT,
                is_verified INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE CASCADE,
                FOREIGN KEY (term_id) REFERENCES terms(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                FOREIGN KEY (type_code) REFERENCES assessment_types(code) ON DELETE CASCADE
            );
        """)

        # 6. Internet qidiruv kesh jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                results_json TEXT NOT NULL,
                found INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                selected_grade INTEGER,
                search_count INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 8. Qidiruv jurnali (statistika va xatolarni tahlil qilish uchun)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                grade_id INTEGER NOT NULL,
                term_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL,
                type_code TEXT NOT NULL,
                assignment_num INTEGER NOT NULL,
                found INTEGER DEFAULT 0,
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 9. Foydalanuvchilarning topilmagan javoblar bo'yicha so'rovlari
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                grade_id INTEGER NOT NULL,
                term_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                type_code TEXT NOT NULL,
                assignment_num INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await db.commit()
        logger.info("Ma'lumotlar bazasi jadvallari muvaffaqiyatli tekshirildi/yaratildi.")
