import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from bot.database.db import get_db

# ----------------- Foydalanuvchilar (Users) -----------------

async def register_or_update_user(user_id: int, username: Optional[str], first_name: str, last_name: Optional[str] = None):
    async with get_db() as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                last_active = CURRENT_TIMESTAMP;
        """, (user_id, username, first_name, last_name))
        await db.commit()

async def update_user_grade(user_id: int, grade_id: int):
    async with get_db() as db:
        await db.execute("""
            UPDATE users SET selected_grade = ?, last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?;
        """, (grade_id, user_id))
        await db.commit()

async def increment_user_search(user_id: int):
    async with get_db() as db:
        await db.execute("""
            UPDATE users SET search_count = search_count + 1, last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?;
        """, (user_id,))
        await db.commit()

async def get_user_stats():
    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) as total_users FROM users;") as cursor:
            row = await cursor.fetchone()
            total_users = row["total_users"] if row else 0

        async with db.execute("SELECT COUNT(*) as active_today FROM users WHERE date(last_active) = date('now');") as cursor:
            row = await cursor.fetchone()
            active_today = row["active_today"] if row else 0

        async with db.execute("SELECT COUNT(*) as total_assignments FROM assignments;") as cursor:
            row = await cursor.fetchone()
            total_assignments = row["total_assignments"] if row else 0

        async with db.execute("SELECT COUNT(*) as total_searches FROM search_logs;") as cursor:
            row = await cursor.fetchone()
            total_searches = row["total_searches"] if row else 0

        async with db.execute("SELECT COUNT(*) as failed_searches FROM search_logs WHERE found = 0;") as cursor:
            row = await cursor.fetchone()
            failed_searches = row["failed_searches"] if row else 0

        return {
            "total_users": total_users,
            "active_today": active_today,
            "total_assignments": total_assignments,
            "total_searches": total_searches,
            "failed_searches": failed_searches
        }

async def get_all_user_ids() -> List[int]:
    async with get_db() as db:
        async with db.execute("SELECT user_id FROM users;") as cursor:
            rows = await cursor.fetchall()
            return [row["user_id"] for row in rows]

# ----------------- Sinflar (Grades) -----------------

async def get_all_grades() -> List[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("SELECT id, name FROM grades ORDER BY id ASC;") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_grade_by_id(grade_id: int) -> Optional[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("SELECT id, name FROM grades WHERE id = ?;", (grade_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

# ----------------- Choraklar (Terms) -----------------

async def get_all_terms() -> List[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("SELECT id, name FROM terms ORDER BY id ASC;") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_term_by_id(term_id: int) -> Optional[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("SELECT id, name FROM terms WHERE id = ?;", (term_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

# ----------------- Fanlar (Subjects) -----------------

async def get_subjects_by_grade(grade_id: int) -> List[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("""
            SELECT id, grade_id, name, code, icon, order_num 
            FROM subjects 
            WHERE grade_id = ? 
            ORDER BY order_num ASC, id ASC;
        """, (grade_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_subject_by_id(subject_id: int) -> Optional[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("SELECT * FROM subjects WHERE id = ?;", (subject_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def add_subject(grade_id: int, name: str, code: str, icon: str = '📖', order_num: int = 0) -> int:
    async with get_db() as db:
        cursor = await db.execute("""
            INSERT INTO subjects (grade_id, name, code, icon, order_num)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(grade_id, code) DO UPDATE SET
                name = excluded.name,
                icon = excluded.icon,
                order_num = excluded.order_num;
        """, (grade_id, name, code, icon, order_num))
        await db.commit()
        return cursor.lastrowid

async def delete_subject(subject_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM subjects WHERE id = ?;", (subject_id,))
        await db.commit()

# ----------------- Baholash turlari (Assessment Types) -----------------

async def get_assessment_types() -> List[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("SELECT code, name, description FROM assessment_types;") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ----------------- Topshiriqlar va Javoblar (Assignments) -----------------

async def get_assignment(grade_id: int, term_id: int, subject_id: int, type_code: str, assignment_num: int) -> Optional[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("""
            SELECT a.*, s.name as subject_name, g.name as grade_name, t.name as term_name
            FROM assignments a
            JOIN subjects s ON a.subject_id = s.id
            JOIN grades g ON a.grade_id = g.id
            JOIN terms t ON a.term_id = t.id
            WHERE a.grade_id = ? AND a.term_id = ? AND a.subject_id = ? 
              AND a.type_code = ? AND a.assignment_num = ?;
        """, (grade_id, term_id, subject_id, type_code, assignment_num)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_assignments_list(grade_id: int, term_id: int, subject_id: int, type_code: str) -> List[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("""
            SELECT id, assignment_num, title, is_verified, (answers_text IS NOT NULL AND LENGTH(answers_text) > 0) as has_answer
            FROM assignments
            WHERE grade_id = ? AND term_id = ? AND subject_id = ? AND type_code = ?
            ORDER BY assignment_num ASC;
        """, (grade_id, term_id, subject_id, type_code)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def add_or_update_assignment(
    grade_id: int,
    term_id: int,
    subject_id: int,
    type_code: str,
    assignment_num: int,
    title: str,
    questions_text: Optional[str],
    answers_text: Optional[str],
    source_url: Optional[str] = None,
    source_name: Optional[str] = "Ochiq manba",
    file_id: Optional[str] = None,
    file_type: Optional[str] = None,
    is_verified: int = 1
) -> int:
    async with get_db() as db:
        # Tekshirish, avval mavjudmi
        async with db.execute("""
            SELECT id FROM assignments
            WHERE grade_id = ? AND term_id = ? AND subject_id = ? AND type_code = ? AND assignment_num = ?;
        """, (grade_id, term_id, subject_id, type_code, assignment_num)) as cursor:
            row = await cursor.fetchone()

        if row:
            assign_id = row["id"]
            await db.execute("""
                UPDATE assignments SET
                    title = ?,
                    questions_text = ?,
                    answers_text = ?,
                    source_url = ?,
                    source_name = ?,
                    file_id = COALESCE(?, file_id),
                    file_type = COALESCE(?, file_type),
                    is_verified = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (title, questions_text, answers_text, source_url, source_name, file_id, file_type, is_verified, assign_id))
            await db.commit()
            return assign_id
        else:
            cursor = await db.execute("""
                INSERT INTO assignments (
                    grade_id, term_id, subject_id, type_code, assignment_num,
                    title, questions_text, answers_text, source_url, source_name,
                    file_id, file_type, is_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                grade_id, term_id, subject_id, type_code, assignment_num,
                title, questions_text, answers_text, source_url, source_name,
                file_id, file_type, is_verified
            ))
            await db.commit()
            return cursor.lastrowid

async def delete_assignment(assignment_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM assignments WHERE id = ?;", (assignment_id,))
        await db.commit()

# ----------------- Kesh (Search Cache) -----------------

async def get_cached_search(cache_key: str, max_age_days: int = 14) -> Optional[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("""
            SELECT results_json, found, last_checked_at,
                   (julianday('now') - julianday(last_checked_at)) as age_days
            FROM search_cache
            WHERE cache_key = ?;
        """, (cache_key,)) as cursor:
            row = await cursor.fetchone()
            if row and row["age_days"] <= max_age_days:
                try:
                    return {
                        "results": json.loads(row["results_json"]),
                        "found": bool(row["found"]),
                        "last_checked_at": row["last_checked_at"]
                    }
                except Exception:
                    return None
            return None

async def set_cached_search(cache_key: str, results: Dict[str, Any], found: bool):
    results_str = json.dumps(results, ensure_ascii=False)
    async with get_db() as db:
        await db.execute("""
            INSERT INTO search_cache (cache_key, results_json, found, last_checked_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(cache_key) DO UPDATE SET
                results_json = excluded.results_json,
                found = excluded.found,
                last_checked_at = CURRENT_TIMESTAMP;
        """, (cache_key, results_str, 1 if found else 0))
        await db.commit()

# ----------------- Log va Xatolar (Search Logs) -----------------

async def log_search(
    user_id: int,
    grade_id: int,
    term_id: int,
    subject_name: str,
    type_code: str,
    assignment_num: int,
    found: bool,
    error_msg: Optional[str] = None
):
    async with get_db() as db:
        await db.execute("""
            INSERT INTO search_logs (
                user_id, grade_id, term_id, subject_name,
                type_code, assignment_num, found, error_msg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (user_id, grade_id, term_id, subject_name, type_code, assignment_num, 1 if found else 0, error_msg))
        await db.commit()

async def get_recent_failed_searches(limit: int = 15) -> List[Dict[str, Any]]:
    async with get_db() as db:
        async with db.execute("""
            SELECT grade_id, term_id, subject_name, type_code, assignment_num, 
                   COUNT(*) as request_count, MAX(created_at) as last_requested
            FROM search_logs
            WHERE found = 0
            GROUP BY grade_id, term_id, subject_name, type_code, assignment_num
            ORDER BY request_count DESC, last_requested DESC
            LIMIT ?;
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ----------------- Foydalanuvchi so'rovi (User Requests) -----------------

async def add_user_request(user_id: int, grade_id: int, term_id: int, subject_id: int, type_code: str, assignment_num: int):
    async with get_db() as db:
        await db.execute("""
            INSERT INTO user_requests (user_id, grade_id, term_id, subject_id, type_code, assignment_num)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (user_id, grade_id, term_id, subject_id, type_code, assignment_num))
        await db.commit()
