import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from bot.database.models import register_or_update_user
from bot.keyboards.homework_kb import get_main_mode_keyboard

logger = logging.getLogger(__name__)
start_router = Router(name="start_router")

START_TEXT = (
    "Assalomu alaykum! 🎓\n\n"
    "<b>O‘zbekiston maktab o‘quvchilari uchun BSB/CHSB va Uyga vazifa yechuvchi botga xush kelibsiz!</b>\n\n"
    "Quyidagi xizmatlardan birini tanlang:\n\n"
    "📊 <b>BSB va CHSB javoblari</b> — 5-sinfdan 11-sinfgacha barcha rasmiy fanlar bo‘yicha summativ baholash yechimlari.\n\n"
    "✍️ <b>Uyga vazifani yechish (AI Ustoz)</b> — kitob yoki daftardagi topshiriq rasmini yoxud matnini yuboring, "
    "bot barcha fanlardan misollarni daftarga ko‘chirib yozishga mos qilib to‘liq yechib beradi!"
)

HELP_TEXT = (
    "📖 <b>Botdan foydalanish bo‘yicha qo‘llanma:</b>\n\n"
    "1. <b>BSB va CHSB bo‘limi:</b>\n"
    "   - Sinfingizni (5–11) va chorakni tanlang;\n"
    "   - Fanni hamda BSB yoki CHSB turini tanlang;\n"
    "   - Bot barcha savollar va ularning to'liq raqamlangan yechimlarini chiqaradi.\n\n"
    "2. <b>Uyga vazifani yechish bo‘limi:</b>\n"
    "   - Kerakli fanni (Matematika, Fizika, Ona tili, Ingliz tili va hk.) tanlang;\n"
    "   - Kitobdagi misol rasmini (fotosini) yuboring yoki topshiriqni chatga yozing;\n"
    "   - Bot daftarga yozishga mos qilib qadamma-qadam to'liq yechib beradi!\n\n"
    "ℹ️ <i>Bot barcha maktab fanlarini qo'llab-quvvatlaydi.</i>"
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

    kb = get_main_mode_keyboard()
    await message.answer(START_TEXT, reply_markup=kb, parse_mode="HTML")

@start_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")

@start_router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    kb = get_main_mode_keyboard()
    await message.answer(START_TEXT, reply_markup=kb, parse_mode="HTML")
