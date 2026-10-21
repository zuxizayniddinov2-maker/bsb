import asyncio
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.config import ADMIN_IDS
from bot.database.models import (
    get_user_stats,
    get_recent_failed_searches,
    get_all_grades,
    get_all_terms,
    get_subjects_by_grade,
    add_or_update_assignment,
    add_subject,
    get_all_user_ids,
)
from bot.database.seed_data import seed_database
from bot.keyboards.admin_kb import (
    AdminCallback,
    get_admin_main_keyboard,
    get_admin_cancel_keyboard,
)

logger = logging.getLogger(__name__)
admin_router = Router(name="admin_router")

# FSM Holatlari (States)
class AddAssignmentFSM(StatesGroup):
    grade_id = State()
    term_id = State()
    subject_id = State()
    type_code = State()
    assignment_num = State()
    title = State()
    questions_text = State()
    answers_text = State()
    source_info = State()
    attachment = State()

class AddSubjectFSM(StatesGroup):
    grade_id = State()
    name = State()
    code = State()
    icon = State()

class BroadcastFSM(StatesGroup):
    message = State()

def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    return user_id in ADMIN_IDS

# Admin paneli bosh menyusi (/admin)
@admin_router.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ <b>Kechirasiz, sizda bot boshqaruv paneliga kirish huquqi yo'q.</b>", parse_mode="HTML")
        return

    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer(
        "🛠 <b>Bot boshqaruv paneliga xush kelibsiz!</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=kb,
        parse_mode="HTML"
    )

# Jarayonni bekor qilish
@admin_router.callback_query(AdminCallback.filter(F.action == "cancel"))
async def cancel_handler(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    kb = get_admin_main_keyboard()
    await query.message.edit_text("❌ Amaliyot bekor qilindi.\n\nBoshqaruv menyusi:", reply_markup=kb)
    await query.answer()

# Menyuni yopish
@admin_router.callback_query(AdminCallback.filter(F.action == "close"))
async def close_handler(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await query.message.delete()
    except Exception:
        await query.message.edit_text("Boshqaruv paneli yopildi.")
    await query.answer()

# 1. Umumiy statistika
@admin_router.callback_query(AdminCallback.filter(F.action == "stats"))
async def stats_handler(query: types.CallbackQuery):
    if not is_admin(query.from_user.id):
        await query.answer("Ruxsat yo'q!", show_alert=True)
        return

    stats = await get_user_stats()
    text = (
        "📊 <b>Botning umumiy ko'rsatkichlari:</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b> ta\n"
        f"⚡ Bugungi faol foydalanuvchilar: <b>{stats['active_today']}</b> ta\n"
        f"📚 Bazadagi tasdiqlangan topshiriqlar: <b>{stats['total_assignments']}</b> ta\n"
        f"🔍 Jami qidiruvlar soni: <b>{stats['total_searches']}</b> marta\n"
        f"⚠️ Topilmagan/xatolik qidiruvlar: <b>{stats['failed_searches']}</b> marta\n"
    )
    kb = get_admin_main_keyboard()
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

# 2. Qidiruv xatolari va foydalanuvchilar talablari
@admin_router.callback_query(AdminCallback.filter(F.action == "failed_searches"))
async def failed_searches_handler(query: types.CallbackQuery):
    if not is_admin(query.from_user.id):
        return

    failed = await get_recent_failed_searches(limit=12)
    if not failed:
        text = "✅ <b>Hozircha hech qanday topilmagan qidiruv xatosi yo'q!</b>"
    else:
        text = "🔍 <b>O‘quvchilar eng ko‘p qidirgan va topilmagan topshiriqlar:</b>\n\n"
        for i, item in enumerate(failed, 1):
            text += (
                f"{i}. <b>{item['grade_id']}-sinf</b> | {item['term_id']}-chorak\n"
                f"   📖 Fan: <i>{item['subject_name']}</i>\n"
                f"   🏷 Topshiriq: <b>{item['assignment_num']}-{item['type_code']}</b>\n"
                f"   🔥 So'rovlar soni: <b>{item['request_count']}</b> marta\n"
                f"   🕒 Oxirgi so'rov: <code>{item['last_requested']}</code>\n\n"
            )

    kb = get_admin_main_keyboard()
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

# 3. Bazani qayta to'ldirish (Reseed)
@admin_router.callback_query(AdminCallback.filter(F.action == "reseed"))
async def reseed_handler(query: types.CallbackQuery):
    if not is_admin(query.from_user.id):
        return

    await query.answer("Qayta yuklanmoqda...")
    await seed_database()
    kb = get_admin_main_keyboard()
    await query.message.edit_text("✅ <b>Baza rasmiy o'quv dasturi bilan muvaffaqiyatli yangilandi!</b>", reply_markup=kb, parse_mode="HTML")

# 4. Fanlar ro'yxatini ko'rish
@admin_router.callback_query(AdminCallback.filter(F.action == "manage_subjects"))
async def manage_subjects_handler(query: types.CallbackQuery):
    if not is_admin(query.from_user.id):
        return

    grades = await get_all_grades()
    text = "📚 <b>Sinflar bo'yicha fanlar taqsimoti:</b>\n\n"
    for g in grades:
        subjects = await get_subjects_by_grade(g["id"])
        sub_names = ", ".join([s["name"] for s in subjects[:4]])
        text += f"🎓 <b>{g['name']}:</b> {len(subjects)} ta fan ({sub_names}...)\n"

    text += "\n<i>Har bir sinf o'zining rasmiy o'quv rejasidagi mustaqil fanlariga ega.</i>"
    kb = get_admin_main_keyboard()
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

# 5. Yangi BSB/CHSB qo'shish (Wizard FSM)
@admin_router.callback_query(AdminCallback.filter(F.action == "add_assign"))
async def start_add_assignment(query: types.CallbackQuery, state: FSMContext):
    if not is_admin(query.from_user.id):
        return

    await state.set_state(AddAssignmentFSM.grade_id)
    kb = get_admin_cancel_keyboard()
    await query.message.edit_text(
        "📝 <b>Yangi topshiriq qo'shish (1/8-qadam)</b>\n\n"
        "Sinf raqamini yozing (masalan: <b>5</b>, <b>7</b>, <b>11</b>):",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@admin_router.message(AddAssignmentFSM.grade_id)
async def process_add_grade(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit() or int(text) not in range(5, 12):
        await message.answer("⚠️ Iltimos, 5 dan 11 gacha bo'lgan to'g'ri sinf raqamini yozing (masalan: 7):")
        return

    await state.update_data(grade_id=int(text))
    await state.set_state(AddAssignmentFSM.term_id)
    await message.answer(
        "📅 <b>Chorak raqamini yozing (1, 2, 3 yoki 4):</b>",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.term_id)
async def process_add_term(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit() or int(text) not in (1, 2, 3, 4):
        await message.answer("⚠️ Iltimos, 1 dan 4 gacha bo'lgan chorak raqamini kiriting:")
        return

    await state.update_data(term_id=int(text))
    data = await state.get_data()
    subjects = await get_subjects_by_grade(data["grade_id"])

    subj_text = "\n".join([f"ID: <code>{s['id']}</code> — {s['name']}" for s in subjects])
    await state.set_state(AddAssignmentFSM.subject_id)
    await message.answer(
        f"📖 <b>Fan ID raqamini tanlang va yuboring:</b>\n\n{subj_text}",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.subject_id)
async def process_add_subject(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, yuqoridagi ro'yxatdan to'g'ri Fan ID raqamini kiriting:")
        return

    await state.update_data(subject_id=int(text))
    await state.set_state(AddAssignmentFSM.type_code)
    await message.answer(
        "🏷 <b>Baholash turini yozing: BSB yoki CHSB</b>",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.type_code)
async def process_add_type(message: types.Message, state: FSMContext):
    text = message.text.strip().upper()
    if text not in ("BSB", "CHSB"):
        await message.answer("⚠️ Faqat BSB yoki CHSB deb yozing:")
        return

    await state.update_data(type_code=text)
    await state.set_state(AddAssignmentFSM.assignment_num)
    await message.answer(
        "🔢 <b>Topshiriq yoki variant raqamini yozing (masalan: 1 yoki 2):</b>",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.assignment_num)
async def process_add_num(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit() or int(text) < 1:
        await message.answer("⚠️ Iltimos, musbat butun son kiriting (masalan: 1):")
        return

    await state.update_data(assignment_num=int(text))
    await state.set_state(AddAssignmentFSM.title)
    await message.answer(
        "📌 <b>Topshiriq sarlavhasini yozing (masalan: 1-BSB: Natural sonlar):</b>",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.title)
async def process_add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddAssignmentFSM.questions_text)
    await message.answer(
        "📋 <b>Topshiriq savollarini kiriting:</b>\n"
        "(Agar bir nechta savol bo'lsa, barcha savollarni bir xabarda yuboring)",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.questions_text)
async def process_add_questions(message: types.Message, state: FSMContext):
    await state.update_data(questions_text=message.text.strip())
    await state.set_state(AddAssignmentFSM.answers_text)
    await message.answer(
        "💡 <b>Topshiriq javoblari va yechimlarini kiriting:</b>",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.answers_text)
async def process_add_answers(message: types.Message, state: FSMContext):
    await state.update_data(answers_text=message.text.strip())
    await state.set_state(AddAssignmentFSM.source_info)
    await message.answer(
        "🌐 <b>Manba havolasini yozing (agar yo'q bo'lsa, 'yoq' deb yozing):</b>",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.source_info)
async def process_add_source(message: types.Message, state: FSMContext):
    text = message.text.strip()
    source_url = None if text.lower() in ("yoq", "yo'q", "yo’q", "no", "-") else text
    await state.update_data(source_url=source_url)

    await state.set_state(AddAssignmentFSM.attachment)
    await message.answer(
        "📎 <b>Topshiriqqa rasm yoki PDF hujjat biriktirasizmi?</b>\n\n"
        "Rasm/PDF faylni yuboring yoki o'tkazib yuborish uchun <b>'otkazish'</b> deb yozing:",
        reply_markup=get_admin_cancel_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(AddAssignmentFSM.attachment)
async def process_add_attachment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_id = None
    file_type = None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"

    assign_id = await add_or_update_assignment(
        grade_id=data["grade_id"],
        term_id=data["term_id"],
        subject_id=data["subject_id"],
        type_code=data["type_code"],
        assignment_num=data["assignment_num"],
        title=data["title"],
        questions_text=data["questions_text"],
        answers_text=data["answers_text"],
        source_url=data.get("source_url"),
        source_name="Admin tomonidan tasdiqlangan",
        file_id=file_id,
        file_type=file_type,
        is_verified=1
    )

    await state.clear()
    kb = get_admin_main_keyboard()
    await message.answer(
        f"✅ <b>Topshiriq muvaffaqiyatli bazaga qo'shildi!</b> (ID: {assign_id})\n\n"
        "Foydalanuvchilar endi ushbu javobni darhol olishlari mumkin.",
        reply_markup=kb,
        parse_mode="HTML"
    )

# 6. Barchaga xabar yuborish (Broadcast)
@admin_router.callback_query(AdminCallback.filter(F.action == "broadcast"))
async def start_broadcast(query: types.CallbackQuery, state: FSMContext):
    if not is_admin(query.from_user.id):
        return

    await state.set_state(BroadcastFSM.message)
    kb = get_admin_cancel_keyboard()
    await query.message.edit_text(
        "📢 <b>Barcha bot foydalanuvchilariga xabar yuborish:</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni yozing (matn, rasm yoki post ko'rinishida):",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@admin_router.message(BroadcastFSM.message)
async def process_broadcast(message: types.Message, state: FSMContext):
    user_ids = await get_all_user_ids()
    await state.clear()

    status_msg = await message.answer(f"⏳ Xabar {len(user_ids)} ta foydalanuvchiga yuborilmoqda...")

    success = 0
    failed = 0

    for uid in user_ids:
        try:
            await message.send_copy(chat_id=uid)
            success += 1
            await asyncio.sleep(0.04)  # Telegram rate limitdan saqlanish
        except Exception:
            failed += 1

    kb = get_admin_main_keyboard()
    await status_msg.edit_text(
        f"📢 <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"✅ Muvaffaqiyatli: <b>{success}</b> ta\n"
        f"❌ Yetkazilmadi (bloklangan/o'chirilgan): <b>{failed}</b> ta",
        reply_markup=kb,
        parse_mode="HTML"
    )
