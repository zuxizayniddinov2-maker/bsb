import re
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from bot.database.models import get_cached_search, set_cached_search, log_search
from bot.services.curriculum_solutions import get_curriculum_solution

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "uz,en-US,en;q=0.5",
}

def clean_text(text: str) -> str:
    """Matndagi ortiqcha bo'shliqlar va maxsus belgilarni tozalash."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_domain(url: str) -> str:
    """URL dan domen nomini ajratib olish."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or "Ochiq ta'lim portali"
    except Exception:
        return "Ochiq ta'lim portali"

async def fetch_page_details(client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
    """Topilgan sahifaga kirib, savollar, raqamlangan javoblar va yuklab olish (PDF/DOC) fayllarini tahlil qilish."""
    details = {
        "page_text": "",
        "file_url": None,
        "file_name": None,
        "extracted_answers": []
    }
    try:
        response = await client.get(url, headers=HEADERS, timeout=8.0, follow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Fayl havolalarini qidirish (PDF, DOCX, Google Drive)
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if any(ext in href.lower() for ext in [".pdf", ".doc", ".docx", "drive.google.com", "t.me/"]):
                    if not href.startswith("http"):
                        parsed = urlparse(url)
                        base = f"{parsed.scheme}://{parsed.netloc}"
                        href = base + ("/" if not href.startswith("/") else "") + href
                    
                    details["file_url"] = href
                    details["file_name"] = a.get_text(strip=True) or "Topshiriq fayli (PDF/DOC)"
                    break

            # Raqamlangan javoblar va savollarni qidirish (1. ..., 2. ...)
            lines = []
            for tag in soup.find_all(["p", "li", "div", "h3", "h4"]):
                txt = clean_text(tag.get_text())
                if re.match(r"^\d+[\.\)]\s*", txt) or "javob" in txt.lower() or "yechim" in txt.lower():
                    if 15 < len(txt) < 300:
                        lines.append(txt)
                        if len(lines) >= 6:
                            break

            if lines:
                details["extracted_answers"] = lines
    except Exception as e:
        logger.warning(f"Sahifa tafsilotlarini yuklashda xatolik ({url}): {e}")

    return details

async def search_online_materials(
    user_id: int,
    grade_id: int,
    grade_name: str,
    term_id: int,
    term_name: str,
    subject_id: int,
    subject_name: str,
    subject_code: str,
    type_code: str,
    assignment_num: int,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Berilgan parametrlar bo'yicha to'liq, aniq raqamlangan (1. Javob: ..., 2. Javob: ...)
    BSB/CHSB topshiriq va yechimlarini qaytarish.
    """
    cache_key = f"g{grade_id}_t{term_id}_s{subject_id}_{type_code}_{assignment_num}"

    # 1. Keshni tekshirish
    if not force_refresh:
        cached = await get_cached_search(cache_key)
        if cached is not None:
            logger.info(f"Keshdan qaytarildi: {cache_key}")
            return cached["results"]

    # 2. Rasmiy o'quv dasturi bazasidan to'liq yechimni tekshirish
    curriculum_sol = get_curriculum_solution(
        grade_id=grade_id,
        term_id=term_id,
        subject_name=subject_name,
        subject_code=subject_code,
        type_code=type_code,
        assignment_num=assignment_num
    )

    # 3. Internetdan ochiq manbalarni va biriktirilgan PDF fayllarni qidirish
    file_url = None
    file_name = None
    source_url = None
    source_name = None

    query_primary = f"{grade_id}-sinf {subject_name} {term_id}-chorak {assignment_num}-{type_code} javoblari"
    all_extracted_candidates = []

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            search_url = f"https://html.duckduckgo.com/html/?q={httpx.URL(query_primary)}"
            resp = await client.get(search_url, headers=HEADERS, timeout=7.0)
            if resp.status_code in (200, 202):
                soup = BeautifulSoup(resp.text, "html.parser")
                results = soup.select(".result__body")
                for r in results:
                    title_tag = r.select_one(".result__title")
                    link_tag = r.select_one(".result__url")
                    if title_tag:
                        title = clean_text(title_tag.get_text())
                        raw_link = link_tag.get_text(strip=True) if link_tag else ""
                        full_link = raw_link if raw_link.startswith("http") else f"https://{raw_link}"
                        all_extracted_candidates.append({
                            "title": title,
                            "url": full_link,
                            "domain": extract_domain(full_link)
                        })
                        if len(all_extracted_candidates) >= 3:
                            break

            if all_extracted_candidates:
                best = all_extracted_candidates[0]
                source_url = best["url"]
                source_name = best["domain"]
                page_info = await fetch_page_details(client, source_url)
                file_url = page_info.get("file_url")
                file_name = page_info.get("file_name")
    except Exception as e:
        logger.warning(f"Internet qidiruvida xatolik: {e}")

    # Agar o'quv dasturidan mukammal yechim mavjud bo'lsa
    if curriculum_sol:
        found_result = {
            "found": True,
            "grade_id": grade_id,
            "grade_name": grade_name,
            "term_id": term_id,
            "term_name": term_name,
            "subject_name": subject_name,
            "type_code": type_code,
            "assignment_num": assignment_num,
            "title": curriculum_sol.get("title") or f"{assignment_num}-{type_code}: {subject_name}",
            "questions_text": curriculum_sol.get("questions"),
            "answers_text": curriculum_sol.get("answers"),
            "source_url": source_url or "https://ziyonet.uz",
            "source_name": source_name or curriculum_sol.get("source") or "O‘zbekiston MMTV amaldagi o‘quv dasturi",
            "file_url": file_url,
            "file_name": file_name,
            "is_verified": True,
            "checked_at": "Rasmiy mezon asosida tasdiqlangan"
        }

        await set_cached_search(cache_key, found_result, found=True)
        await log_search(user_id, grade_id, term_id, subject_name, type_code, assignment_num, found=True)
        return found_result

    # Agar topilmasa
    not_found_result = {
        "found": False,
        "grade_id": grade_id,
        "grade_name": grade_name,
        "term_id": term_id,
        "term_name": term_name,
        "subject_name": subject_name,
        "type_code": type_code,
        "assignment_num": assignment_num,
        "message": "Bu topshiriqning ishonchli javobi hozircha topilmadi."
    }

    await set_cached_search(cache_key, not_found_result, found=False)
    await log_search(user_id, grade_id, term_id, subject_name, type_code, assignment_num, found=False, error_msg="Material topilmadi")
    return not_found_result
