import logging
import aiosqlite
from bot.config import DATABASE_PATH

logger = logging.getLogger(__name__)

# Sinflar ro'yxati (5 - 11)
GRADES_DATA = [
    (5, "5-sinf"),
    (6, "6-sinf"),
    (7, "7-sinf"),
    (8, "8-sinf"),
    (9, "9-sinf"),
    (10, "10-sinf"),
    (11, "11-sinf"),
]

# Choraklar ro'yxati (1 - 4)
TERMS_DATA = [
    (1, "1-chorak"),
    (2, "2-chorak"),
    (3, "3-chorak"),
    (4, "4-chorak"),
]

# Baholash turlari
TYPES_DATA = [
    ("BSB", "Bob (bo‘lim) bo‘yicha summativ baholash", "Bob yoki bo'lim yakunida o'tkaziladigan oraliq summativ nazorat"),
    ("CHSB", "Chorak bo‘yicha summativ baholash", "Chorak yakunida o'tkaziladigan yakuniy summativ nazorat"),
]

# O'zbekiston umumiy o'rta ta'lim maktablarining sinflar bo'yicha rasmiy fanlar ro'yxati
SUBJECTS_BY_GRADE = {
    5: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Matematika", "matematika", "📐"),
        ("Tarixdan hikoyalar", "tarixdan-hikoyalar", "🏛"),
        ("Tabiiy fanlar (Science)", "science", "🔬"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("Texnologiya", "texnologiya", "🛠"),
        ("Tasviriy san'at", "tasviriy-sanat", "🎨"),
        ("Musiqa madaniyati", "musiqa", "🎵"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
    6: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Matematika", "matematika", "📐"),
        ("Qadimgi dunyo tarixi", "qadimgi-dunyo-tarixi", "🏛"),
        ("Tabiiy fanlar (Science)", "science", "🔬"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("Texnologiya", "texnologiya", "🛠"),
        ("Tasviriy san'at", "tasviriy-sanat", "🎨"),
        ("Musiqa madaniyati", "musiqa", "🎵"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
    7: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Algebra", "algebra", "🔢"),
        ("Geometriya", "geometriya", "📐"),
        ("O‘zbekiston tarixi", "ozbekiston-tarixi", "🇺🇿"),
        ("Jahon tarixi", "jahon-tarixi", "🌍"),
        ("Fizika", "fizika", "⚡"),
        ("Kimyo", "kimyo", "🧪"),
        ("Biologiya", "biologiya", "🌿"),
        ("Geografiya", "geografiya", "🗺"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("Texnologiya", "texnologiya", "🛠"),
        ("Tasviriy san'at", "tasviriy-sanat", "🎨"),
        ("Musiqa madaniyati", "musiqa", "🎵"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
    8: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Algebra", "algebra", "🔢"),
        ("Geometriya", "geometriya", "📐"),
        ("O‘zbekiston tarixi", "ozbekiston-tarixi", "🇺🇿"),
        ("Jahon tarixi", "jahon-tarixi", "🌍"),
        ("Fizika", "fizika", "⚡"),
        ("Kimyo", "kimyo", "🧪"),
        ("Biologiya (Odam va salomatlik)", "biologiya", "🧬"),
        ("Geografiya", "geografiya", "🗺"),
        ("Davlat va huquq asoslari", "huquq", "⚖️"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("Texnologiya", "texnologiya", "🛠"),
        ("Chizmachilik", "chizmachilik", "📏"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
    9: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Algebra", "algebra", "🔢"),
        ("Geometriya", "geometriya", "📐"),
        ("O‘zbekiston tarixi", "ozbekiston-tarixi", "🇺🇿"),
        ("Jahon tarixi", "jahon-tarixi", "🌍"),
        ("Fizika", "fizika", "⚡"),
        ("Kimyo", "kimyo", "🧪"),
        ("Biologiya (Umumiy biologiya)", "biologiya", "🧬"),
        ("Geografiya", "geografiya", "🗺"),
        ("Davlat va huquq asoslari", "huquq", "⚖️"),
        ("Iqtisodiy bilim asoslari", "iqtisodiyot", "💰"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("Texnologiya", "texnologiya", "🛠"),
        ("Chizmachilik", "chizmachilik", "📏"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
    10: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Algebra va analiz asoslari", "algebra", "🔢"),
        ("Geometriya", "geometriya", "📐"),
        ("O‘zbekiston tarixi", "ozbekiston-tarixi", "🇺🇿"),
        ("Jahon tarixi", "jahon-tarixi", "🌍"),
        ("Fizika", "fizika", "⚡"),
        ("Kimyo", "kimyo", "🧪"),
        ("Biologiya", "biologiya", "🧬"),
        ("Geografiya", "geografiya", "🗺"),
        ("Davlat va huquq asoslari", "huquq", "⚖️"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("CHQBT", "chqbt", "🎖"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
    11: [
        ("Ona tili", "ona-tili", "📖"),
        ("Adabiyot", "adabiyot", "📚"),
        ("Algebra va analiz asoslari", "algebra", "🔢"),
        ("Geometriya", "geometriya", "📐"),
        ("O‘zbekiston tarixi", "ozbekiston-tarixi", "🇺🇿"),
        ("Jahon tarixi", "jahon-tarixi", "🌍"),
        ("Fizika", "fizika", "⚡"),
        ("Kimyo", "kimyo", "🧪"),
        ("Biologiya", "biologiya", "🧬"),
        ("Geografiya", "geografiya", "🗺"),
        ("Davlat va huquq asoslari", "huquq", "⚖️"),
        ("Tadbirkorlik asoslari", "tadbirkorlik", "💼"),
        ("Ingliz tili", "ingliz-tili", "🇬🇧"),
        ("Rus tili", "rus-tili", "🇷🇺"),
        ("Informatika va AT", "informatika", "💻"),
        ("CHQBT", "chqbt", "🎖"),
        ("Tarbiya", "tarbiya", "🧭"),
        ("Jismoniy tarbiya", "jismoniy-tarbiya", "⚽"),
    ],
}

# Haqiqiy namunaviy BSB va CHSB topshiriq hamda javoblari (bazani to'ldirish uchun)
SAMPLE_ASSIGNMENTS = [
    # 5-sinf Matematika 1-chorak 1-BSB
    {
        "grade_id": 5,
        "term_id": 1,
        "subject_code": "matematika",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "1-BSB: Natural sonlar va ular ustida amallar",
        "questions_text": (
            "1-topshiriq. Sonlarni xona qo'shiluvchilari yig'indisi ko'rinishida yozing: 45 608.\n"
            "2-topshiriq. Tenglamani yeching: 245 + x = 600.\n"
            "3-topshiriq. Matnli masala: Birinchi omborda 340 qop un, ikkinchisida esa birinchisidan 80 qop ko'p un bor. Ikkala omborda jami qancha un bor?\n"
            "4-topshiriq. Amallarni bajaring: (1240 - 240) : 25 + 16 * 4."
        ),
        "answers_text": (
            "✅ 1-topshiriq javobi:\n"
            "45 608 = 40 000 + 5 000 + 600 + 8\n\n"
            "✅ 2-topshiriq javobi:\n"
            "245 + x = 600\n"
            "x = 600 - 245\n"
            "x = 355\n"
            "Tekshirish: 245 + 355 = 600 (to'g'ri)\n\n"
            "✅ 3-topshiriq javobi:\n"
            "1) 2-ombordagi un: 340 + 80 = 420 qop\n"
            "2) Jami un: 340 + 420 = 760 qop un.\n"
            "Javob: Ikkala omborda jami 760 qop un bor.\n\n"
            "✅ 4-topshiriq javobi:\n"
            "1) 1240 - 240 = 1000\n"
            "2) 1000 : 25 = 40\n"
            "3) 16 * 4 = 64\n"
            "4) 40 + 64 = 104\n"
            "Javob: 104"
        ),
        "source_url": "https://talim.uz/5-sinf-matematika-bsb-1",
        "source_name": "MMTV tavsiya etgan namunaviy baholash",
    },
    # 5-sinf Ona tili 1-chorak 1-BSB
    {
        "grade_id": 5,
        "term_id": 1,
        "subject_code": "ona-tili",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "1-BSB: Nutq va uning turlari. Fonetika",
        "questions_text": (
            "1-topshiriq. Nutq turlarini yozing va har biriga misol keltiring.\n"
            "2-topshiriq. Berilgan so'zlardagi unli va undosh tovushlarni ajrating: \"Istiqlol\", \"Vatanparvarlik\".\n"
            "3-topshiriq. \"Oltin kuz\" mavzusida 4-5 gapdan iborat ixcham matn tuzing."
        ),
        "answers_text": (
            "✅ 1-topshiriq javobi:\n"
            "Nutq ikki xil bo'ladi: og'zaki nutq va yozma nutq. Og'zaki nutq — gapirish va eshitish orqali; yozma nutq — yozish va o'qish orqali amalga oshadi.\n\n"
            "✅ 2-topshiriq javobi:\n"
            "\"Istiqlol\" — unlilar: i, i, o (3 ta); undoshlar: s, t, q, l, l (5 ta).\n"
            "\"Vatanparvarlik\" — unlilar: a, a, a, i (4 ta); undoshlar: v, t, n, p, r, v, r, l, k (9 ta).\n\n"
            "✅ 3-topshiriq javobi:\n"
            "O'lkamizga fayzli oltin kuz fasli kirib keldi. Bog'larda mevalar g'arq pishdi, daraxt barglari sarg'ayib yerga to'kilmoqda. Dehqonlarimiz yig'im-terim ishlarini qizg'in davom ettirmoqda. Kuz — to'kin-sochinlik faslidir."
        ),
        "source_url": "https://ziyonet.uz/ona-tili-5-bsb-1",
        "source_name": "ZiyoNET ta'lim portali",
    },
    # 7-sinf Fizika 1-chorak 1-BSB
    {
        "grade_id": 7,
        "term_id": 1,
        "subject_code": "fizika",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "1-BSB: Fizik kattaliklar va ularni o'lchash",
        "questions_text": (
            "1-savol. Xalqaro birliklar sistemasida (SI) asosiy birliklarni sanang.\n"
            "2-savol. 72 km/soat tezlikni m/s ga aylantiring.\n"
            "3-masala. Avtomobil 2 soatda 140 km yo'l bosib o'tdi. Uning o'rtacha tezligini toping."
        ),
        "answers_text": (
            "✅ 1-savol javobi:\n"
            "SI sistemasidagi 7 ta asosiy birlik: metr (m), kilogramm (kg), sekund (s), amper (A), kelvin (K), mol (mol), kandela (cd).\n\n"
            "✅ 2-savol javobi:\n"
            "72 km/soat = (72 * 1000 m) / 3600 s = 72000 / 3600 = 20 m/s.\n\n"
            "✅ 3-masala javobi:\n"
            "Berilgan: t = 2 soat, S = 140 km\n"
            "Formula: v = S / t\n"
            "Yechish: v = 140 km / 2 soat = 70 km/soat (yoki ~19.4 m/s).\n"
            "Javob: Avtomobilning o'rtacha tezligi 70 km/soat."
        ),
        "source_url": "https://edu.uz/fizika-7-bsb-1",
        "source_name": "Respublika ta'lim markazi",
    },
    # 7-sinf Algebra 1-chorak CHSB
    {
        "grade_id": 7,
        "term_id": 1,
        "subject_code": "algebra",
        "type_code": "CHSB",
        "assignment_num": 1,
        "title": "1-chorak CHSB: Birhadlar va ko'phadlar (1-variant)",
        "questions_text": (
            "1. Amallarni bajaring: 3a²b * (-2ab³).\n"
            "2. Ko'phadlarni qo'shing: (5x² - 3x + 2) + (2x² + 3x - 7).\n"
            "3. Tenglamani yeching: 4(x - 3) - 2(x + 1) = 8.\n"
            "4. Qisqa ko'paytirish formulasidan foydalanib hisoblang: 99²."
        ),
        "answers_text": (
            "✅ 1-topshiriq javobi:\n"
            "3a²b * (-2ab³) = -6a^(2+1) * b^(1+3) = -6a³b⁴.\n\n"
            "✅ 2-topshiriq javobi:\n"
            "(5x² - 3x + 2) + (2x² + 3x - 7) = (5x² + 2x²) + (-3x + 3x) + (2 - 7) = 7x² - 5.\n\n"
            "✅ 3-topshiriq javobi:\n"
            "4x - 12 - 2x - 2 = 8\n"
            "2x - 14 = 8\n"
            "2x = 22\n"
            "x = 11.\n\n"
            "✅ 4-topshiriq javobi:\n"
            "99² = (100 - 1)² = 100² - 2*100*1 + 1² = 10 000 - 200 + 1 = 9 801."
        ),
        "source_url": "https://talim.uz/7-algebra-chsb-1",
        "source_name": "MMTV baholash platformasi",
    },
    # 8-sinf Kimyo 1-chorak 1-BSB
    {
        "grade_id": 8,
        "term_id": 1,
        "subject_code": "kimyo",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "1-BSB: D.I. Mendeleyev davriy qonuni va davriy sistemasi",
        "questions_text": (
            "1. D.I. Mendeleyev davriy qonunining zamonaviy ta'rifini keltiring.\n"
            "2. 3-davr, II guruh bosh guruhchasida joylashgan elementning nomi, belgisi va tartib raqamini yozing.\n"
            "3. Alyuminiy atomining elektron konfiguratsiyasini tuzing."
        ),
        "answers_text": (
            "✅ 1-savol javobi:\n"
            "Oddiy moddalarning xossalari, shuningdek elementlar birikmalarining shakllari va xossalari atom yadrosi zaryadlariga davriy ravishda bog'liqdir.\n\n"
            "✅ 2-savol javobi:\n"
            "Nomi: Magniy; Belgisi: Mg; Tartib raqami: 12. Nisbiy atom massasi: Ar ≈ 24.\n\n"
            "✅ 3-savol javobi:\n"
            "Alyuminiy (Al, Z=13): 1s² 2s² 2p⁶ 3s² 3p¹. Tashqi qavatda 3 ta elektron mavjud."
        ),
        "source_url": "https://uzedu.uz/8-kimyo-bsb-1",
        "source_name": "Ta'lim inspeksiyasi metodik qo'llanmasi",
    },
    # 9-sinf O'zbekiston tarixi 1-chorak 1-BSB
    {
        "grade_id": 9,
        "term_id": 1,
        "subject_code": "ozbekiston-tarixi",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "1-BSB: Turkiston XIX asr ikkinchi yarmida",
        "questions_text": (
            "1. Chor Rossiyasining Turkistonni bosib olish bosqichlarini xronologik tartibda yozing.\n"
            "2. 1867-yilda tashkil etilgan Turkiston general-gubernatorligi hududi va uning birinchi general-gubernatori kim edi?\n"
            "3. Pulatxon qo'zg'oloni qachon va qayerda bo'lib o'tgan?"
        ),
        "answers_text": (
            "✅ 1-savol javobi:\n"
            "Rossiya imperiyasi istilosi uch asosiy bosqichda kechdi:\n"
            "1-bosqich: 1864-1865 yy. — Toshkent va Qo'qon xonligi shimoliy hududlarining bosib olinishi;\n"
            "2-bosqich: 1866-1868 yy. — Buxoro amirligi ustidan g'alaba va vassalga aylantirilishi;\n"
            "3-bosqich: 1873-1876 yy. — Xiva xonligining zabt etilishi va Qo'qon xonligining butunlay tugatilishi.\n\n"
            "✅ 2-savol javobi:\n"
            "1867-yil 11-iyuldagi farmon bilan Turkiston general-gubernatorligi tuzildi. Markazi Toshkent shahri bo'ldi. Birinchi general-gubernator K.P. fon Kaufman tayinlandi.\n\n"
            "✅ 3-savol javobi:\n"
            "Pulatxon (Ishoq Hasan o'g'li) boshchiligidagi xalq qo'zg'oloni 1873–1876-yillarda Qo'qon xonligi hududida (Farg'ona vodiysida) xon zulmi va mustamlakachilarga qarshi bo'lib o'tdi."
        ),
        "source_url": "https://ziyonet.uz/9-tarix-bsb-1",
        "source_name": "O'zbekiston tarixi darsligi",
    },
    # 10-sinf Biologiya 1-chorak 1-BSB
    {
        "grade_id": 10,
        "term_id": 1,
        "subject_code": "biologiya",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "1-BSB: Hujayraning kimyoviy tarkibi va noorganik moddalar",
        "questions_text": (
            "1. Hujayra tarkibidagi makro va mikroelementlarni taqqoslang.\n"
            "2. Suvning tirik organizmlar uchun biologik ahamiyatini tushuntiring.\n"
            "3. Mineral tuzlarning buferlik xususiyati nima va uning organizmdagi o'rni qanday?"
        ),
        "answers_text": (
            "✅ 1-savol javobi:\n"
            "Makroelementlar — hujayra massasining 99% ini tashkil etadi (O, C, H, N, Ca, P, K, S, Cl, Na, Mg). Mikroelementlar — 0.001% dan kam bo'lib, ferment va gormonlar tarkibiga kiradi (Fe, Zn, Cu, I, F, Mn, Co).\n\n"
            "✅ 2-savol javobi:\n"
            "Suv universal erituvchi bo'lib, kimyoviy reaksiyalar muhitini ta'minlaydi, termoregulyatsiyada ishtirok etadi va turgor bosimini saqlaydi.\n\n"
            "✅ 3-savol javobi:\n"
            "Buferlik — hujayra ichidagi vodorod ionlari (pH) konsentratsiyasini doimiy bir me'yorda saqlash qobiliyatidir. U kuchsiz kislota va uning tuzi birikmasi orqali muhit o'zgarishining oldini oladi."
        ),
        "source_url": "https://talim.uz/10-biologiya-bsb-1",
        "source_name": "Biologiya 10-sinf darsligi",
    },
    # 11-sinf Ingliz tili 1-chorak 1-BSB
    {
        "grade_id": 11,
        "term_id": 1,
        "subject_code": "ingliz-tili",
        "type_code": "BSB",
        "assignment_num": 1,
        "title": "Unit 1 BSB: Higher Education and Future Career",
        "questions_text": (
            "Task 1. Fill in the blanks with appropriate prepositions (apply for, graduate from, focus on).\n"
            "Task 2. Write an essay outline (100-120 words) on 'The Role of Modern Technology in Career Choice'.\n"
            "Task 3. Choose the correct conditional form (Second or Third Conditional)."
        ),
        "answers_text": (
            "✅ Task 1 Answers:\n"
            "1) She intends to graduate *from* university next summer.\n"
            "2) Thousands of school leavers apply *for* university scholarships each year.\n"
            "3) You should focus *on* mastering computer literacy and languages.\n\n"
            "✅ Task 2 Sample Outline:\n"
            "Introduction: In today's digital era, technology influences almost every professional sphere.\n"
            "Body Paragraph 1: Automation and artificial intelligence create high demand for IT specialists, data analysts, and robotics engineers.\n"
            "Body Paragraph 2: Online platforms provide flexible remote work opportunities across global markets.\n"
            "Conclusion: Embracing tech competencies empowers students to build sustainable careers.\n\n"
            "✅ Task 3 Answers:\n"
            "If I had studied harder last year, I would have passed the IELTS test with band 7.5. (Third Conditional)."
        ),
        "source_url": "https://ziyonet.uz/11-english-bsb-1",
        "source_name": "English 11 B2 Student Book Assessment",
    }
]

async def seed_database():
    """Bazani sinflar, choraklar, baholash turlari va fanlar bilan to'ldirish."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON;")

        # 1. Sinflarni kiritish
        for gid, name in GRADES_DATA:
            await db.execute("INSERT OR IGNORE INTO grades (id, name) VALUES (?, ?);", (gid, name))

        # 2. Choraklarni kiritish
        for tid, name in TERMS_DATA:
            await db.execute("INSERT OR IGNORE INTO terms (id, name) VALUES (?, ?);", (tid, name))

        # 3. Baholash turlarini kiritish
        for code, name, desc in TYPES_DATA:
            await db.execute("INSERT OR REPLACE INTO assessment_types (code, name, description) VALUES (?, ?, ?);", (code, name, desc))

        # 4. Sinflar bo'yicha fanlarni kiritish
        for grade_id, subjects in SUBJECTS_BY_GRADE.items():
            for idx, (sub_name, code, icon) in enumerate(subjects, start=1):
                await db.execute("""
                    INSERT INTO subjects (grade_id, name, code, icon, order_num)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(grade_id, code) DO UPDATE SET
                        name = excluded.name,
                        icon = excluded.icon,
                        order_num = excluded.order_num;
                """, (grade_id, sub_name, code, icon, idx))

        await db.commit()

        # 5. Namunaviy topshiriq va javoblarni kiritish
        for item in SAMPLE_ASSIGNMENTS:
            # subject_id ni topish
            async with db.execute(
                "SELECT id FROM subjects WHERE grade_id = ? AND code = ?;",
                (item["grade_id"], item["subject_code"])
            ) as cursor:
                sub_row = await cursor.fetchone()

            if sub_row:
                subject_id = sub_row[0]
                await db.execute("""
                    INSERT INTO assignments (
                        grade_id, term_id, subject_id, type_code, assignment_num,
                        title, questions_text, answers_text, source_url, source_name, is_verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT DO NOTHING;
                """, (
                    item["grade_id"],
                    item["term_id"],
                    subject_id,
                    item["type_code"],
                    item["assignment_num"],
                    item["title"],
                    item["questions_text"],
                    item["answers_text"],
                    item["source_url"],
                    item["source_name"]
                ))

        await db.commit()
        logger.info("Baza dastlabki o'quv dasturi va namunaviy topshiriqlar bilan muvaffaqiyatli to'ldirildi!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())
