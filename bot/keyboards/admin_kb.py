from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from typing import Optional

class AdminCallback(CallbackData, prefix="adm"):
    action: str
    target_id: Optional[int] = 0

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli menyusi."""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Umumiy statistika", callback_data=AdminCallback(action="stats").pack()),
            InlineKeyboardButton(text="➕ BSB/CHSB qo‘shish", callback_data=AdminCallback(action="add_assign").pack()),
        ],
        [
            InlineKeyboardButton(text="🔍 Qidiruv xatolari & Talablar", callback_data=AdminCallback(action="failed_searches").pack()),
            InlineKeyboardButton(text="📚 Fanlar ro‘yxati", callback_data=AdminCallback(action="manage_subjects").pack()),
        ],
        [
            InlineKeyboardButton(text="📢 Barchaga xabar yuborish", callback_data=AdminCallback(action="broadcast").pack()),
            InlineKeyboardButton(text="🔄 Bazani qayta yuklash", callback_data=AdminCallback(action="reseed").pack()),
        ],
        [
            InlineKeyboardButton(text="❌ Menyuni yopish", callback_data=AdminCallback(action="close").pack())
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_cancel_keyboard() -> InlineKeyboardMarkup:
    """Jarayonni bekor qilish tugmasi."""
    buttons = [
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=AdminCallback(action="cancel").pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
