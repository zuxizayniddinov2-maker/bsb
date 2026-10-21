import logging
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest

from bot.database.models import (
    get_all_grades,
    get_grade_by_id,
    get_all_terms,
    get_term_by_id,
    get_subjects_by_grade,
    get_subject_by_id,
    get_assignment,
    get_assignments_list,
    update_user_grade,
    increment_user_search,
    add_user_request,
)
from bot.keyboards.inline import (
    GradeCallback,
    TermCallback,
    SubjectCallback,
    SubjectPageCallback,
    TypeCallback,
    AssignmentCallback,
    ActionCallback,
    get_grades_keyboard,
    get_terms_keyboard,
    get_subjects_keyboard,
    get_types_keyboard,
    get_assignments_keyboard,
    get_result_keyboard,
)
from bot.services.search_service import search_online_materials
from bot.utils.helpers import format_assignment_text, format_not_found_text
from bot.handlers.start import START_TEXT

logger = logging.getLogger(__name__)
student_router = Router(name="student_router")


# 1. Sinf tanlanganda (Grade selection)
@student_router.callback_query(GradeCallback.filter())
async def process_grade_select(query: types.CallbackQuery, callback_data: GradeCallback):
    grade_id = callback_data.grade_id
    await update_user_grade(query.from_user.id, grade_id)

    grade = await get_grade_by_id(grade_id)
    grade_name = grade["name"] if grade else f"{grade_id}-sinf"

    terms = await get_all_terms()
    kb = get_terms_keyboard(grade_id, terms)

    text = f"📚 <b>{grade_name}</b> tanlandi.\n\nChorakni tanlang:"
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


# 2. Chorak tanlanganda (Term selection)
@student_router.callback_query(TermCallback.filter())
async def process_term_select(query: types.CallbackQuery, callback_data: TermCallback):
    grade_id = callback_data.grade_id
    term_id = callback_data.term_id

    grade = await get_grade_by_id(grade_id)
    term = await get_term_by_id(term_id)
    grade_name = grade["name"] if grade else f"{grade_id}-sinf"
    term_name = term["name"] if term else f"{term_id}-chorak"

    subjects = await get_subjects_by_grade(grade_id)
    kb = get_subjects_keyboard(grade_id, term_id, subjects, page=0)

    text = f"📚 <b>{grade_name}</b> | 📅 <b>{term_name}</b>\n\nFanni tanlang:"
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


# 3. Fanlar sahifasini almashtirganda (Subject pagination)
@student_router.callback_query(SubjectPageCallback.filter())
async def process_subject_page(query: types.CallbackQuery, callback_data: SubjectPageCallback):
    grade_id = callback_data.grade_id
    term_id = callback_data.term_id
    page = callback_data.page

    subjects = await get_subjects_by_grade(grade_id)
    kb = get_subjects_keyboard(grade_id, term_id, subjects, page=page)

    try:
        await query.message.edit_reply_markup(reply_markup=kb)
    except TelegramBadRequest:
        pass
    await query.answer()


# 4. Fan tanlanganda (Subject selection -> BSB yoki CHSB turini tanlash)
@student_router.callback_query(SubjectCallback.filter())
async def process_subject_select(query: types.CallbackQuery, callback_data: SubjectCallback):
    grade_id = callback_data.grade_id
    term_id = callback_data.term_id
    subject_id = callback_data.subject_id

    grade = await get_grade_by_id(grade_id)
    term = await get_term_by_id(term_id)
    subject = await get_subject_by_id(subject_id)

    grade_name = grade["name"] if grade else f"{grade_id}-sinf"
    term_name = term["name"] if term else f"{term_id}-chorak"
    subject_name = subject["name"] if subject else "Tanlangan fan"

    kb = get_types_keyboard(grade_id, term_id, subject_id)
    text = (
        f"📚 <b>{grade_name}</b> | 📅 <b>{term_name}</b>\n"
        f"📖 Fan: <b>{subject_name}</b>\n\n"
        f"Topshiriq turini tanlang:"
    )

    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


# 5. Baholash turi tanlanganda (Type selection: BSB yoki CHSB -> Topshiriq raqami)
@student_router.callback_query(TypeCallback.filter())
async def process_type_select(query: types.CallbackQuery, callback_data: TypeCallback):
    grade_id = callback_data.grade_id
    term_id = callback_data.term_id
    subject_id = callback_data.subject_id
    type_code = callback_data.type_code

    grade = await get_grade_by_id(grade_id)
    term = await get_term_by_id(term_id)
    subject = await get_subject_by_id(subject_id)

    grade_name = grade["name"] if grade else f"{grade_id}-sinf"
    term_name = term["name"] if term else f"{term_id}-chorak"
    subject_name = subject["name"] if subject else "Fan"

    # Bazadagi mavjud topshiriqlarni olish
    db_assignments = await get_assignments_list(grade_id, term_id, subject_id, type_code)
    kb = get_assignments_keyboard(grade_id, term_id, subject_id, type_code, db_assignments, subject_name=subject_name)

    text = (
        f"📚 <b>{grade_name}</b> | 📅 <b>{term_name}</b>\n"
        f"📖 Fan: <b>{subject_name}</b>\n"
        f"🏷 Tur: <b>{type_code}</b>\n\n"
        f"Topshiriqni tanlang:"
    )

    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


# 6. Topshiriq raqami tanlanganda (Assignment selected -> Qidirish va ko'rsatish)
@student_router.callback_query(AssignmentCallback.filter())
async def process_assignment_select(query: types.CallbackQuery, callback_data: AssignmentCallback):
    grade_id = callback_data.grade_id
    term_id = callback_data.term_id
    subject_id = callback_data.subject_id
    type_code = callback_data.type_code
    assignment_num = callback_data.assignment_num

    await query.answer("🔍 Qidirilmoqda, kuting...")

    grade = await get_grade_by_id(grade_id)
    term = await get_term_by_id(term_id)
    subject = await get_subject_by_id(subject_id)

    grade_name = grade["name"] if grade else f"{grade_id}-sinf"
    term_name = term["name"] if term else f"{term_id}-chorak"
    subject_name = subject["name"] if subject else "Fan"
    subject_code = subject["code"] if subject else ""

    # A. Avval mahalliy bazani tekshirish
    db_assign = await get_assignment(grade_id, term_id, subject_id, type_code, assignment_num)

    if db_assign and db_assign.get("answers_text"):
        await increment_user_search(query.from_user.id)
        
        # Agar rasm yoki hujjat fayli biriktirilgan bo'lsa
        file_id = db_assign.get("file_id")
        file_type = db_assign.get("file_type")

        text = format_assignment_text(db_assign)
        kb = get_result_keyboard(
            grade_id, term_id, subject_id, type_code, assignment_num,
            source_url=db_assign.get("source_url"), found=True
        )

        if file_id and file_type == "photo":
            try:
                await query.message.delete()
            except Exception:
                pass
            await query.message.answer_photo(photo=file_id, caption=text[:1024], reply_markup=kb, parse_mode="HTML")
            return
        elif file_id and file_type == "document":
            try:
                await query.message.delete()
            except Exception:
                pass
            await query.message.answer_document(document=file_id, caption=text[:1024], reply_markup=kb, parse_mode="HTML")
            return
        else:
            try:
                await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
            except TelegramBadRequest:
                await query.message.answer(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
            return

    # B. Bazada topilmasa, internetdan va o'quv dasturidan qidirish
    search_data = await search_online_materials(
        user_id=query.from_user.id,
        grade_id=grade_id,
        grade_name=grade_name,
        term_id=term_id,
        term_name=term_name,
        subject_id=subject_id,
        subject_name=subject_name,
        subject_code=subject_code,
        type_code=type_code,
        assignment_num=assignment_num,
        force_refresh=False
    )

    await increment_user_search(query.from_user.id)

    if search_data.get("found"):
        text = format_assignment_text(search_data)
        kb = get_result_keyboard(
            grade_id, term_id, subject_id, type_code, assignment_num,
            source_url=search_data.get("source_url"), found=True
        )
    else:
        text = format_not_found_text(
            grade_name=grade_name,
            term_name=term_name,
            subject_name=subject_name,
            type_code=type_code,
            assignment_num=assignment_num
        )
        kb = get_result_keyboard(
            grade_id, term_id, subject_id, type_code, assignment_num,
            source_url=None, found=False
        )

    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
    except TelegramBadRequest:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)


# 7. Harakatlar (Bosh menyu, Qayta qidirish, Adminga so'rov)
@student_router.callback_query(ActionCallback.filter())
async def process_action(query: types.CallbackQuery, callback_data: ActionCallback):
    action = callback_data.action

    if action == "main_menu":
        grades = await get_all_grades()
        kb = get_grades_keyboard(grades)
        try:
            await query.message.edit_text(START_TEXT, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await query.message.answer(START_TEXT, reply_markup=kb, parse_mode="HTML")
        await query.answer()

    elif action == "retry":
        await query.answer("🔄 Yangilanmoqda...")
        grade_id = callback_data.grade_id
        term_id = callback_data.term_id
        subject_id = callback_data.subject_id
        type_code = callback_data.type_code
        assignment_num = callback_data.assignment_num

        grade = await get_grade_by_id(grade_id)
        term = await get_term_by_id(term_id)
        subject = await get_subject_by_id(subject_id)

        grade_name = grade["name"] if grade else f"{grade_id}-sinf"
        term_name = term["name"] if term else f"{term_id}-chorak"
        subject_name = subject["name"] if subject else "Fan"
        subject_code = subject["code"] if subject else ""

        search_data = await search_online_materials(
            user_id=query.from_user.id,
            grade_id=grade_id,
            grade_name=grade_name,
            term_id=term_id,
            term_name=term_name,
            subject_id=subject_id,
            subject_name=subject_name,
            subject_code=subject_code,
            type_code=type_code,
            assignment_num=assignment_num,
            force_refresh=True
        )

        if search_data.get("found"):
            text = format_assignment_text(search_data)
            kb = get_result_keyboard(
                grade_id, term_id, subject_id, type_code, assignment_num,
                source_url=search_data.get("source_url"), found=True
            )
        else:
            text = format_not_found_text(
                grade_name=grade_name,
                term_name=term_name,
                subject_name=subject_name,
                type_code=type_code,
                assignment_num=assignment_num
            )
            kb = get_result_keyboard(
                grade_id, term_id, subject_id, type_code, assignment_num,
                source_url=None, found=False
            )

        try:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
        except TelegramBadRequest:
            pass

    elif action == "request_admin":
        await add_user_request(
            user_id=query.from_user.id,
            grade_id=callback_data.grade_id,
            term_id=callback_data.term_id,
            subject_id=callback_data.subject_id,
            type_code=callback_data.type_code,
            assignment_num=callback_data.assignment_num
        )
        await query.answer(
            "✅ So‘rovingiz qabul qilindi!\nAdminlarimiz ushbu topshiriqni tez orada bazaga kiritadilar.",
            show_alert=True
        )
