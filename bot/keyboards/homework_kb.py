from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

class ModeCallback(CallbackData, prefix="mode"):
    target: str  # 'bsb_chsb' yoki 'homework'

class HomeworkSubjectCallback(CallbackData, prefix="hw_sub"):
    subject_code: str
    subject_name: str

class HomeworkActionCallback(CallbackData, prefix="hw_act"):
    action: str  # 'retry', 'change_sub', 'main_menu'
    subject_code: str = ""
    subject_name: str = ""

def get_main_mode_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu: BSB/CHSB yoki Uyga vazifani tanlash."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📊 BSB va CHSB javoblari",
                callback_data=ModeCallback(target="bsb_chsb").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="✍️ Uyga vazifani yechish (AI Ustoz)",
                callback_data=ModeCallback(target="homework").pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Maktabdagi barcha asosiy fanlar
ALL_HOMEWORK_SUBJECTS = [
    ("Matematika / Algebra", "matematika", "📐"),
    ("Geometriya", "geometriya", "📐"),
    ("Ona tili", "ona-tili", "📖"),
    ("Adabiyot", "adabiyot", "📚"),
    ("Fizika", "fizika", "⚡"),
    ("Kimyo", "kimyo", "🧪"),
    ("Biologiya", "biologiya", "🧬"),
    ("Tarix", "tarix", "🏛"),
    ("Ingliz tili", "ingliz-tili", "🇬🇧"),
    ("Rus tili", "rus-tili", "🇷🇺"),
    ("Informatika va AT", "informatika", "💻"),
    ("Geografiya", "geografiya", "🗺"),
    ("Boshqa fanlar", "boshqa", "🧭")
]

def get_homework_subjects_keyboard() -> InlineKeyboardMarkup:
    """Uy vazifasi uchun fanlarni tanlash klaviaturasi."""
    buttons = []
    row = []

    for name, code, icon in ALL_HOMEWORK_SUBJECTS:
        btn = InlineKeyboardButton(
            text=f"{icon} {name}",
            callback_data=HomeworkSubjectCallback(subject_code=code, subject_name=name).pack()
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Bosh menyuga qaytish
    buttons.append([
        InlineKeyboardButton(
            text="🏠 Bosh menyu",
            callback_data=HomeworkActionCallback(action="main_menu").pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_homework_waiting_keyboard() -> InlineKeyboardMarkup:
    """Topshiriq yuborish kutish holatidagi klaviatura."""
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️ Fanlarni almashtirish",
                callback_data=HomeworkActionCallback(action="change_sub").pack()
            ),
            InlineKeyboardButton(
                text="🏠 Bosh menyu",
                callback_data=HomeworkActionCallback(action="main_menu").pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_homework_result_keyboard(subject_name: str, subject_code: str) -> InlineKeyboardMarkup:
    """Yechim chiqqandan keyingi harakatlar."""
    buttons = [
        [
            InlineKeyboardButton(
                text="🔄 Yana misol yuborish",
                callback_data=HomeworkSubjectCallback(subject_code=subject_code, subject_name=subject_name).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="📚 Boshqa fanni tanlash",
                callback_data=HomeworkActionCallback(action="change_sub").pack()
            ),
            InlineKeyboardButton(
                text="🏠 Bosh menyu",
                callback_data=HomeworkActionCallback(action="main_menu").pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
