import html
from typing import Optional, Dict, Any

def format_assignment_text(data: Dict[str, Any]) -> str:
    """BSB / CHSB natijasini chiroyli va tushunarli matn holida formatlash."""
    grade_name = data.get("grade_name") or f"{data.get('grade_id')}-sinf"
    term_name = data.get("term_name") or f"{data.get('term_id')}-chorak"
    subject_name = data.get("subject_name", "")
    type_code = data.get("type_code", "")
    assignment_num = data.get("assignment_num", 1)
    
    is_verified = data.get("is_verified", False)
    badge = "✅ [Tasdiqlangan rasmiy javob]" if is_verified else "🌐 [Internet ochiq manbalaridan olindi]"

    questions = data.get("questions_text") or "Savollar matni manba sahifasida keltirilgan."
    answers = data.get("answers_text") or "Yechimlar to'liq shaklda manbada ko'rsatilgan."
    source_name = data.get("source_name") or "Ochiq ta'lim manbasi"
    source_url = data.get("source_url") or ""

    # Telegram xabari chegarasi 4096 belgi
    if len(questions) > 1200:
        questions = questions[:1190] + "..."
    if len(answers) > 1800:
        answers = answers[:1790] + "..."

    msg = (
        f"📚 <b>{grade_name}</b> | 📅 <b>{term_name}</b>\n"
        f"📖 <b>Fan:</b> {subject_name}\n"
        f"🏷 <b>Tur:</b> {assignment_num}-{type_code}\n"
        f"🛡 <b>Holat:</b> {badge}\n"
        f"────────────────────\n\n"
        f"📋 <b>Topshiriq savollari:</b>\n"
        f"<blockquote>{html.escape(questions)}</blockquote>\n\n"
        f"💡 <b>Topilgan javoblar va yechimlar:</b>\n"
        f"<blockquote>{html.escape(answers)}</blockquote>\n"
    )

    if data.get("file_url"):
        msg += f"\n📎 <b>Biriktirilgan fayl/PDF:</b> <a href=\"{data['file_url']}\">Yuklab olish</a>\n"

    if source_url:
        msg += f"\n🌐 <b>Manba:</b> <a href=\"{source_url}\">{html.escape(source_name)}</a>"

    return msg

def format_not_found_text(
    grade_name: str,
    term_name: str,
    subject_name: str,
    type_code: str,
    assignment_num: int
) -> str:
    """Material topilmaganda chiqariladigan aniq va xolis xabar."""
    return (
        f"📚 <b>{grade_name}</b> | 📅 <b>{term_name}</b>\n"
        f"📖 <b>Fan:</b> {subject_name}\n"
        f"🏷 <b>Topshiriq:</b> {assignment_num}-{type_code}\n"
        f"────────────────────\n\n"
        f"⚠️ <b>Bu topshiriqning ishonchli javobi hozircha topilmadi.</b>\n\n"
        f"Bot ochiq internet manbalarini va ta'lim portallarini qidirdi, "
        f"ammo mazkur topshiriq uchun to'liq va ishonchli javob aniqlanmadi.\n\n"
        f"📌 <i>Eslatma: Maktab baholash tizimi talabiga binoan, tekshirilmagan yoki noto'g'ri "
        f"javoblar o'quvchilarga ko'rsatilmaydi.</i>\n\n"
        f"Siz pastdagi tugma orqali bot ma'muriyatiga ushbu javobni bazaga kiritishni so'rab buyurtma qoldirishingiz mumkin."
    )
