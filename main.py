import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import BOT_TOKEN, DATABASE_PATH
from bot.database.db import init_db
from bot.database.seed_data import seed_database
from bot.handlers.start import start_router
from bot.handlers.student import student_router
from bot.handlers.admin import admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("BSB_CHSB_BOT")

async def setup_bot_commands(bot: Bot):
    """Telegram menyusi uchun standart buyruqlarni o'rnatish."""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish va sinf tanlash"),
        BotCommand(command="menu", description="Asosiy menyuga qaytish"),
        BotCommand(command="help", description="Qo'llanma va ma'lumot"),
        BotCommand(command="admin", description="Admin paneli (faqat adminlar uchun)"),
    ]
    await bot.set_my_commands(commands)

async def main():
    logger.info("Bot ishga tushirilmoqda...")

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "XATOLIK: BOT_TOKEN aniqlanmadi!\n"
            "Iltimos, loyiha papkasidagi '.env' faylini oching va @BotFather orqali olingan tokeningizni kiriting:\n"
            "BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ\n"
            "=" * 60
        )
        return

    # 1. Ma'lumotlar bazasini tayyorlash va o'quv dasturi bilan to'ldirish
    logger.info("Ma'lumotlar bazasi tekshirilmoqda...")
    await init_db()
    await seed_database()

    # 2. Aiogram Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Routerlarni ro'yxatdan o'tkazish
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(student_router)

    # 4. Bot buyruqlarini sozlash va eskirgan yangilanishlarni tozalash
    await setup_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} (ID: {bot_info.id})")
    print(f"\n>>> Bot ishlamoqda! Telegramdan @{bot_info.username} ga /start yuboring.\n")

    # 5. Pollingni boshlash
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
