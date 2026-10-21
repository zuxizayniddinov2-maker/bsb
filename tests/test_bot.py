import asyncio
import os
import unittest
from bot.database.db import init_db
from bot.database.seed_data import seed_database
from bot.database.models import (
    get_all_grades,
    get_all_terms,
    get_subjects_by_grade,
    get_assignment,
    get_user_stats,
    register_or_update_user,
    set_cached_search,
    get_cached_search,
)
from bot.keyboards.inline import (
    get_grades_keyboard,
    get_terms_keyboard,
    get_subjects_keyboard,
    get_types_keyboard,
    get_assignments_keyboard,
)
from bot.utils.helpers import format_assignment_text, format_not_found_text

class TestBotFunctionality(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_db()
        await seed_database()

    async def test_grades_and_terms(self):
        grades = await get_all_grades()
        self.assertEqual(len(grades), 7, "5-sinfdan 11-sinfgacha 7 ta sinf bo'lishi kerak")
        
        grade_ids = [g["id"] for g in grades]
        self.assertEqual(grade_ids, [5, 6, 7, 8, 9, 10, 11])

        terms = await get_all_terms()
        self.assertEqual(len(terms), 4, "4 ta chorak bo'lishi kerak")

    async def test_distinct_curriculum_per_grade(self):
        """Har bir sinfning fanlar ro'yxati alohida va haqiqiy ekanligini tekshirish."""
        g5_subs = [s["name"] for s in await get_subjects_by_grade(5)]
        g7_subs = [s["name"] for s in await get_subjects_by_grade(7)]
        g10_subs = [s["name"] for s in await get_subjects_by_grade(10)]
        g11_subs = [s["name"] for s in await get_subjects_by_grade(11)]

        # 5-sinfda Matematika bor, lekin Algebra/Geometriya yo'q
        self.assertIn("Matematika", g5_subs)
        self.assertNotIn("Algebra", g5_subs)

        # 7-sinfda Algebra, Geometriya, Fizika, Kimyo bor
        self.assertIn("Algebra", g7_subs)
        self.assertIn("Geometriya", g7_subs)
        self.assertIn("Fizika", g7_subs)
        self.assertIn("Kimyo", g7_subs)

        # 10-sinfda CHQBT bor, 5-sinfda yo'q
        self.assertIn("CHQBT", g10_subs)
        self.assertNotIn("CHQBT", g5_subs)

        # 11-sinfda Tadbirkorlik asoslari bor
        self.assertIn("Tadbirkorlik asoslari", g11_subs)

    async def test_sample_assignments_exist(self):
        """Namunaviy kiritilgan BSB va CHSB larning bazada mavjudligini tekshirish."""
        subjects_7 = await get_subjects_by_grade(7)
        fizika_sub = next(s for s in subjects_7 if s["code"] == "fizika")

        assign = await get_assignment(
            grade_id=7,
            term_id=1,
            subject_id=fizika_sub["id"],
            type_code="BSB",
            assignment_num=1
        )
        self.assertIsNotNone(assign)
        self.assertIn("Fizik kattaliklar", assign["title"])
        self.assertTrue(len(assign["answers_text"]) > 20)

    async def test_user_flow_and_stats(self):
        await register_or_update_user(user_id=99999999, username="test_student", first_name="Ali")
        stats = await get_user_stats()
        self.assertGreaterEqual(stats["total_users"], 1)

    async def test_cache_system(self):
        test_key = "test_cache_key_123"
        data = {"title": "Test BSB", "answers": "Test javob"}
        await set_cached_search(test_key, data, found=True)

        cached = await get_cached_search(test_key)
        self.assertIsNotNone(cached)
        self.assertTrue(cached["found"])
        self.assertEqual(cached["results"]["title"], "Test BSB")

    async def test_keyboard_generation(self):
        grades = await get_all_grades()
        kb_grades = get_grades_keyboard(grades)
        self.assertGreater(len(kb_grades.inline_keyboard), 3)

        terms = await get_all_terms()
        kb_terms = get_terms_keyboard(5, terms)
        self.assertEqual(len(kb_terms.inline_keyboard), 3)

        subjects = await get_subjects_by_grade(7)
        kb_subs = get_subjects_keyboard(7, 1, subjects, page=0)
        self.assertGreater(len(kb_subs.inline_keyboard), 1)

    def test_text_formatting(self):
        dummy_data = {
            "grade_name": "7-sinf",
            "term_name": "1-chorak",
            "subject_name": "Fizika",
            "type_code": "BSB",
            "assignment_num": 1,
            "questions_text": "Savollar 1, 2, 3",
            "answers_text": "Javoblar 1, 2, 3",
            "source_name": "MMTV",
            "source_url": "https://talim.uz",
            "is_verified": True
        }
        formatted = format_assignment_text(dummy_data)
        self.assertIn("7-sinf", formatted)
        self.assertIn("Fizika", formatted)
        self.assertIn("Tasdiqlangan rasmiy javob", formatted)

        not_found = format_not_found_text("5-sinf", "2-chorak", "Matematika", "BSB", 3)
        self.assertIn("ishonchli javobi hozircha topilmadi", not_found)

if __name__ == "__main__":
    unittest.main()
