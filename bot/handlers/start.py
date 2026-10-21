import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from bot.database.models import register_or_update_user, get_all_grades
from bot.keyboards.inline import get_grades_keyboard

logger = logging.getLogger(__name__)
start_router = Router(name="start_router")

START_TEXT = (
    "Assalomu alaykum! 🎓\n\n"
    "<b>O‘zbekiston maktab o‘quvchilari uchun BSB va CHSB javoblari botiga xush kelibsiz!</b>\n\n"
    "Bu yerda siz 5-sinfdan 11-sinfgacha bo‘lgan barcha fanlardan Bob bo‘yicha summativ baholash (BSB) "
    "va Choraklik summativ baholash (CHSB) topshiriqlari hamda ularning javoblarini topishingiz mumkin.\n\n"
    "👇 <b>Sinfingizni tanlang:</b>"
)

HELP_TEXT = (
    "📖 <b>Botdan foydalanish bo‘yicha qo‘llanma:</b>\n\n"
    "1. /start buyrug‘ini bosing.\n"
    "2. O‘zingiz o‘qiydigan sinfni (5–11) tanlang.\n"
    "3. O‘quv choragini (1–4) belgilang.\n"
    "4. Fanlar ro‘yxatidan kerakli fanni tanlang.\n"
    "5. Baholash turini (BSB yoki CHSB) va topshiriq raqamini bosing.\n"
    "6. Bot bazadan va internetdan ishonchli yechimlarni topib beradi.\n\n"
    "ℹ️ <i>Bot faqat haqiqiy o‘quv dasturiga mos materiallarni ko‘rsatadi. "
    "Agar javob hali tasdiqlanmagan bo‘lsa, u haqida ochiq ma'lumot beriladi.</i>"
)

@start_router.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user
    await register_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    grades = await get_all_grades()
    kb = get_grades_keyboard(grades)
    await message.answer(START_TEXT, reply_markup=kb, parse_mode="HTML")

@start_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")

@start_router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    grades = await get_all_grades()
    kb = get_grades_keyboard(grades)
    await message.answer("Assalomu alaykum! Sinfingizni tanlang:", reply_markup=kb)
