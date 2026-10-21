import io
import html
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

from bot.keyboards.homework_kb import (
    ModeCallback,
    HomeworkSubjectCallback,
    HomeworkActionCallback,
    get_main_mode_keyboard,
    get_homework_subjects_keyboard,
    get_homework_waiting_keyboard,
    get_homework_result_keyboard,
)
from bot.keyboards.inline import get_grades_keyboard
from bot.database.models import get_all_grades
from bot.services.homework_solver import solve_homework_task
from bot.handlers.start import START_TEXT

logger = logging.getLogger(__name__)
homework_router = Router(name="homework_router")

class HomeworkFSM(StatesGroup):
    waiting_for_task = State()


# 1. Bosh menyudan "BSB va CHSB" yoki "Uyga vazifa" tanlanganda
@homework_router.callback_query(ModeCallback.filter())
async def process_mode_select(query: types.CallbackQuery, callback_data: ModeCallback, state: FSMContext):
    await state.clear()
    target = callback_data.target

    if target == "bsb_chsb":
        grades = await get_all_grades()
        kb = get_grades_keyboard(grades)
        text = (
            "📊 <b>BSB va CHSB bo‘limi tanlandi!</b>\n\n"
            "5-sinfdan 11-sinfgacha bo‘lgan barcha rasmiy fanlar bo‘yicha topshiriqlar va yechimlar.\n\n"
            "👇 <b>Sinfingizni tanlang:</b>"
        )
        try:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await query.answer()

    elif target == "homework":
        kb = get_homework_subjects_keyboard()
        text = (
            "✍️ <b>Uy vazifasini yechish (AI Ustoz) bo‘limi</b>\n\n"
            "Qaysi fandan uy vazifangizni yechmoqchisiz? Quyidagi fanlardan birini tanlang:\n\n"
            "<i>(Istalgan fandan kitobdagi misol rasmini yoki matnini yuborsangiz, bot uni daftarga yozishga tayyor qilib yechib beradi!)</i>"
        )
        try:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await query.answer()


# 2. Uy vazifasi uchun fan tanlanganda
@homework_router.callback_query(HomeworkSubjectCallback.filter())
async def process_homework_subject_select(
    query: types.CallbackQuery,
    callback_data: HomeworkSubjectCallback,
    state: FSMContext
):
    subject_code = callback_data.subject_code
    subject_name = callback_data.subject_name

    await state.update_data(subject_code=subject_code, subject_name=subject_name)
    await state.set_state(HomeworkFSM.waiting_for_task)

    kb = get_homework_waiting_keyboard()
    text = (
        f"📖 <b>{subject_name}</b> fani tanlandi!\n\n"
        f"📸 <b>Topshiriqni yuboring:</b>\n"
        f"1. Kitob yoki daftardagi misol/mashqning <b>rasmini (fotosini)</b> yuborishingiz mumkin.\n"
        f"2. Yoki topshiriq matnini/raqamini <b>chatga yozib yuborishingiz</b> mumkin.\n\n"
        f"<i>Bot topshiriqni to‘liq tahlil qilib, daftarga ko‘chirib yozishga mos qilib qadamma-qadam yechib beradi! ✍️</i>"
    )

    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


# 3. Foydalanuvchi RASM yuborganda (Photo handler)
@homework_router.message(HomeworkFSM.waiting_for_task, F.photo)
async def process_homework_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subject_name = data.get("subject_name", "Matematika")
    subject_code = data.get("subject_code", "matematika")

    wait_msg = await message.answer(
        f"⏳ <b>{subject_name}</b> fanidan rasm qabul qilindi. Topshiriq tahlil qilinmoqda va yechilmoqda, kuting...",
        parse_mode="HTML"
    )

    try:
        # Eng katta sifatdagi rasmni yuklab olish
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes_io = io.BytesIO()
        await message.bot.download_file(file_info.file_path, destination=file_bytes_io)
        image_bytes = file_bytes_io.getvalue()

        caption_text = message.caption or None

        # AI yechuvchi xizmatini chaqirish
        solution = await solve_homework_task(
            subject_name=subject_name,
            text=caption_text,
            image_bytes=image_bytes
        )

        kb = get_homework_result_keyboard(subject_name=subject_name, subject_code=subject_code)

        result_header = (
            f"📚 <b>Fan:</b> {subject_name}\n"
            f"📝 <b>Uyga vazifa yechimi:</b>\n"
            f"────────────────────\n"
            f"✍️ <b>Daftarga yozish uchun to‘liq yechim:</b>\n\n"
        )
        result_footer = (
            f"\n────────────────────\n"
            f"💡 <i>Barcha misollar qadamma-qadam daftarga moslab yechildi.</i>"
        )

        full_text = result_header + solution + result_footer

        # Telegram 4096 belgi chegarasini hisobga olish
        if len(full_text) > 4000:
            # Bo'lib yuborish
            await wait_msg.delete()
            parts = [full_text[i:i+3800] for i in range(0, len(full_text), 3800)]
            for idx, part in enumerate(parts):
                reply_markup = kb if idx == len(parts) - 1 else None
                await message.answer(part, reply_markup=reply_markup)
        else:
            await wait_msg.edit_text(full_text, reply_markup=kb)

    except Exception as e:
        logger.error(f"Rasmdan uy vazifasini yechishda xatolik: {e}")
        kb = get_homework_waiting_keyboard()
        await wait_msg.edit_text(
            "⚠️ <b>Rasmni tahlil qilishda xatolik yuz berdi.</b>\n\n"
            "Iltimos, rasm aniq va yorug' tushganligiga ishonch hosil qilib qaytadan yuboring yoki misol matnini chatga yozing.",
            reply_markup=kb,
            parse_mode="HTML"
        )


# 4. Foydalanuvchi MATN yuborganda (Text handler)
@homework_router.message(HomeworkFSM.waiting_for_task, F.text)
async def process_homework_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subject_name = data.get("subject_name", "Matematika")
    subject_code = data.get("subject_code", "matematika")

    user_text = message.text.strip()

    wait_msg = await message.answer(
        f"⏳ <b>{subject_name}</b> fanidan topshiriq tahlil qilinmoqda va yechilmoqda...",
        parse_mode="HTML"
    )

    try:
        solution = await solve_homework_task(
            subject_name=subject_name,
            text=user_text,
            image_bytes=None
        )

        kb = get_homework_result_keyboard(subject_name=subject_name, subject_code=subject_code)

        result_header = (
            f"📚 <b>Fan:</b> {subject_name}\n"
            f"📝 <b>Uyga vazifa yechimi:</b>\n"
            f"────────────────────\n"
            f"✍️ <b>Daftarga yozish uchun to‘liq yechim:</b>\n\n"
        )
        result_footer = (
            f"\n────────────────────\n"
            f"💡 <i>Topshiriq qadamma-qadam daftarga moslab yechildi.</i>"
        )

        full_text = result_header + solution + result_footer

        if len(full_text) > 4000:
            await wait_msg.delete()
            parts = [full_text[i:i+3800] for i in range(0, len(full_text), 3800)]
            for idx, part in enumerate(parts):
                reply_markup = kb if idx == len(parts) - 1 else None
                await message.answer(part, reply_markup=reply_markup)
        else:
            await wait_msg.edit_text(full_text, reply_markup=kb)

    except Exception as e:
        logger.error(f"Matndan uy vazifasini yechishda xatolik: {e}")
        kb = get_homework_waiting_keyboard()
        await wait_msg.edit_text(
            "⚠️ <b>Topshiriqni yechishda xatolik yuz berdi.</b>\n"
            "Iltimos, qaytadan yuboring.",
            reply_markup=kb,
            parse_mode="HTML"
        )


# 5. Uy vazifasi navigatsiya tugmalari (Harakatlar)
@homework_router.callback_query(HomeworkActionCallback.filter())
async def process_homework_actions(
    query: types.CallbackQuery,
    callback_data: HomeworkActionCallback,
    state: FSMContext
):
    action = callback_data.action

    if action == "change_sub":
        await state.clear()
        kb = get_homework_subjects_keyboard()
        text = (
            "📚 <b>Fanni tanlang:</b>\n\n"
            "Qaysi fandan uy vazifangizni yechmoqchisiz?"
        )
        try:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await query.answer()

    elif action == "main_menu":
        await state.clear()
        kb = get_main_mode_keyboard()
        try:
            await query.message.edit_text(START_TEXT, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await query.message.answer(START_TEXT, reply_markup=kb, parse_mode="HTML")
        await query.answer()
