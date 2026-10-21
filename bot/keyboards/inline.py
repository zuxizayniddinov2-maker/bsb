from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

# Callback Data Factories
class GradeCallback(CallbackData, prefix="gr"):
    grade_id: int

class TermCallback(CallbackData, prefix="tm"):
    grade_id: int
    term_id: int

class SubjectPageCallback(CallbackData, prefix="sp"):
    grade_id: int
    term_id: int
    page: int

class SubjectCallback(CallbackData, prefix="sb"):
    grade_id: int
    term_id: int
    subject_id: int

class TypeCallback(CallbackData, prefix="tp"):
    grade_id: int
    term_id: int
    subject_id: int
    type_code: str  # 'BSB' yoki 'CHSB'

class AssignmentCallback(CallbackData, prefix="as"):
    grade_id: int
    term_id: int
    subject_id: int
    type_code: str
    assignment_num: int

class ActionCallback(CallbackData, prefix="act"):
    action: str  # 'main_menu', 'retry', 'request_admin'
    grade_id: Optional[int] = 0
    term_id: Optional[int] = 0
    subject_id: Optional[int] = 0
    type_code: Optional[str] = ""
    assignment_num: Optional[int] = 0


def get_grades_keyboard(grades: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """1. Sinfni tanlash klaviaturasi (5-sinfdan 11-sinfgacha)."""
    buttons = []
    row = []
    for g in sorted(grades, key=lambda x: x["id"]):
        btn = InlineKeyboardButton(
            text=f"🎓 {g['name']}",
            callback_data=GradeCallback(grade_id=g["id"]).pack()
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_terms_keyboard(grade_id: int, terms: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """2. Chorakni tanlash klaviaturasi."""
    buttons = []
    row = []
    for t in sorted(terms, key=lambda x: x["id"]):
        btn = InlineKeyboardButton(
            text=f"📅 {t['name']}",
            callback_data=TermCallback(grade_id=grade_id, term_id=t["id"]).pack()
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Navigatsiya tugmalari
    nav_row = [
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data=ActionCallback(action="main_menu").pack()
        ),
        InlineKeyboardButton(
            text="🏠 Bosh menyu",
            callback_data=ActionCallback(action="main_menu").pack()
        )
    ]
    buttons.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subjects_keyboard(
    grade_id: int,
    term_id: int,
    subjects: List[Dict[str, Any]],
    page: int = 0,
    per_page: int = 6
) -> InlineKeyboardMarkup:
    """3. Fanlarni tanlash klaviaturasi (sahifalangan holda)."""
    total_subjects = len(subjects)
    total_pages = max(1, (total_subjects + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))

    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_subjects = subjects[start_idx:end_idx]

    buttons = []
    row = []
    for s in current_subjects:
        icon = s.get("icon") or "📖"
        btn = InlineKeyboardButton(
            text=f"{icon} {s['name']}",
            callback_data=SubjectCallback(grade_id=grade_id, term_id=term_id, subject_id=s["id"]).pack()
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Sahifalash tugmalari (agar bir nechta sahifa bo'lsa)
    if total_pages > 1:
        page_nav = []
        if page > 0:
            page_nav.append(InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=SubjectPageCallback(grade_id=grade_id, term_id=term_id, page=page - 1).pack()
            ))
        page_nav.append(InlineKeyboardButton(
            text=f"📄 {page + 1}/{total_pages}",
            callback_data="noop"
        ))
        if page < total_pages - 1:
            page_nav.append(InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=SubjectPageCallback(grade_id=grade_id, term_id=term_id, page=page + 1).pack()
            ))
        buttons.append(page_nav)

    # Orqaga va Bosh menyu tugmalari
    nav_row = [
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data=GradeCallback(grade_id=grade_id).pack()
        ),
        InlineKeyboardButton(
            text="🏠 Bosh menyu",
            callback_data=ActionCallback(action="main_menu").pack()
        )
    ]
    buttons.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_types_keyboard(grade_id: int, term_id: int, subject_id: int) -> InlineKeyboardMarkup:
    """4. BSB yoki CHSB turini tanlash klaviaturasi."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📝 BSB (Bob baholash)",
                callback_data=TypeCallback(grade_id=grade_id, term_id=term_id, subject_id=subject_id, type_code="BSB").pack()
            ),
            InlineKeyboardButton(
                text="📑 CHSB (Chorak baholash)",
                callback_data=TypeCallback(grade_id=grade_id, term_id=term_id, subject_id=subject_id, type_code="CHSB").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data=TermCallback(grade_id=grade_id, term_id=term_id).pack()
            ),
            InlineKeyboardButton(
                text="🏠 Bosh menyu",
                callback_data=ActionCallback(action="main_menu").pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subject_bsb_count(subject_name: str = "") -> int:
    """O'zbekiston maktab o'quv dasturi bo'yicha fanning chorakdagi BSB sonini aniqlash."""
    name_lower = subject_name.lower()
    # 3-5 soatlik asosiy fanlar: Matematika, Algebra, Ona tili, Ingliz tili -> 3 ta BSB
    three_bsb_subjects = ["matematika", "algebra", "ona tili", "ona-tili", "ingliz", "english"]
    if any(k in name_lower for k in three_bsb_subjects):
        return 3
    # 1-2 soatlik barcha fanlar: Fizika, Kimyo, Biologiya, Tarix, Geografiya, Adabiyot va hk. -> 2 ta BSB
    return 2


def get_assignments_keyboard(
    grade_id: int,
    term_id: int,
    subject_id: int,
    type_code: str,
    db_assignments: List[Dict[str, Any]],
    subject_name: str = ""
) -> InlineKeyboardMarkup:
    """5. Topshiriq raqamini tanlash klaviaturasi (faqat haqiqiy BSB va CHSB soni bo'yicha)."""
    # Bazadagi mavjud topshiriqlar raqamlarini to'plash
    existing_nums = {item["assignment_num"]: item for item in db_assignments}

    buttons = []
    row = []

    if type_code == "BSB":
        # Maktab dasturida fanga qarab aniq 2 yoki 3 ta BSB bo'ladi
        max_bsb = get_subject_bsb_count(subject_name)
        available_numbers = list(range(1, max_bsb + 1))
        # Agar bazada admin tomonidan qo'shilgan boshqa raqam bo'lsa
        for num in existing_nums:
            if num not in available_numbers:
                available_numbers.append(num)
        available_numbers.sort()

        for num in available_numbers:
            verified_mark = " ✅" if num in existing_nums and existing_nums[num].get("has_answer") else ""
            btn = InlineKeyboardButton(
                text=f"📝 {num}-BSB{verified_mark}",
                callback_data=AssignmentCallback(
                    grade_id=grade_id, term_id=term_id, subject_id=subject_id,
                    type_code=type_code, assignment_num=num
                ).pack()
            )
            row.append(btn)
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

    else:  # CHSB
        # Har chorakda 1 ta CHSB bo'ladi (1-variant va 2-variant)
        chsb_options = [
            (1, "📑 CHSB (1-variant)"),
            (2, "📑 CHSB (2-variant)")
        ]
        for num, label in chsb_options:
            verified_mark = " ✅" if num in existing_nums and existing_nums[num].get("has_answer") else ""
            btn = InlineKeyboardButton(
                text=f"{label}{verified_mark}",
                callback_data=AssignmentCallback(
                    grade_id=grade_id, term_id=term_id, subject_id=subject_id,
                    type_code=type_code, assignment_num=num
                ).pack()
            )
            buttons.append([btn])

    # Navigatsiya
    nav_row = [
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data=SubjectCallback(grade_id=grade_id, term_id=term_id, subject_id=subject_id).pack()
        ),
        InlineKeyboardButton(
            text="🏠 Bosh menyu",
            callback_data=ActionCallback(action="main_menu").pack()
        )
    ]
    buttons.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_result_keyboard(
    grade_id: int,
    term_id: int,
    subject_id: int,
    type_code: str,
    assignment_num: int,
    source_url: Optional[str] = None,
    found: bool = True
) -> InlineKeyboardMarkup:
    """6. Natija chiqqandan keyingi klaviatura."""
    buttons = []

    action_row = []
    if source_url and (source_url.startswith("http://") or source_url.startswith("https://")):
        action_row.append(InlineKeyboardButton(text="🌐 Manbani ochish", url=source_url))

    action_row.append(
        InlineKeyboardButton(
            text="🔄 Qayta qidirish",
            callback_data=ActionCallback(
                action="retry",
                grade_id=grade_id,
                term_id=term_id,
                subject_id=subject_id,
                type_code=type_code,
                assignment_num=assignment_num
            ).pack()
        )
    )
    buttons.append(action_row)

    if not found:
        # Topilmagan bo'lsa adminga so'rov yuborish
        buttons.append([
            InlineKeyboardButton(
                text="📩 Adminga buyurtma berish",
                callback_data=ActionCallback(
                    action="request_admin",
                    grade_id=grade_id,
                    term_id=term_id,
                    subject_id=subject_id,
                    type_code=type_code,
                    assignment_num=assignment_num
                ).pack()
            )
        ])

    # Navigatsiya
    nav_row = [
        InlineKeyboardButton(
            text="⬅️ Topshiriqlarga qaytish",
            callback_data=TypeCallback(
                grade_id=grade_id, term_id=term_id, subject_id=subject_id, type_code=type_code
            ).pack()
        ),
        InlineKeyboardButton(
            text="🏠 Bosh menyu",
            callback_data=ActionCallback(action="main_menu").pack()
        )
    ]
    buttons.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
