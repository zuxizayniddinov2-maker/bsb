# 🎓 O‘zbekiston maktab o‘quvchilari uchun BSB va CHSB javoblari Telegram boti

O‘zbekiston Respublikasi umumiy o‘rta ta’lim maktablarining **5-sinfidan 11-sinfigacha** bo‘lgan o‘quvchilari uchun **Bob bo‘yicha summativ baholash (BSB)** va **Choraklik summativ baholash (CHSB)** topshiriqlari hamda ularning yechimlarini topib beruvchi to‘liq backend va ma’lumotlar bazasiga ega Telegram bot.

---

## 🌟 Asosiy imkoniyatlar

1. **Sinflar bo‘yicha to‘liq qamrov (5–11-sinflar):**
   - 5-sinfdan 11-sinfgacha bo‘lgan barcha sinflar qamrab olingan.
   - Har bir sinf uchun O‘zbekiston Maktabgacha va maktab ta’limi vazirligi (MMTV) tomonidan tasdiqlangan rasmiy o‘quv dasturidagi alohida fanlar ro‘yxati shakllantirilgan (umumiy bitta ro‘yxat emas, har bir sinf uchun mustaqil fanlar).

2. **Choraklar (1–4-choraklar):**
   - O‘quv yilining barcha 4 ta choragi bo‘yicha topshiriqlar ajratilgan.

3. **Baholash turlari:**
   - **BSB:** Bob/bo‘lim yakunidagi oraliq summativ nazoratlar (1-BSB, 2-BSB, 3-BSB, 4-BSB va hk.).
   - **CHSB:** Chorak yakunidagi yakuniy summativ nazoratlar (1-variant, 2-variant, namunaviy testlar).

4. **Aqlli qidiruv va ma’lumotlar bazasi (Database & Smart Search):**
   - Bot avval o‘zining tezkor mahalliy ma’lumotlar bazasidan tasdiqlangan javoblarni tekshiradi.
   - Agar bazada mavjud bo‘lmasa, bot server tomonidan internetdagi ochiq ta’lim portallari (ZiyoNET, EduPortal, bsb-chsb.com, bilimmarkazi va boshqalar) orqali maqsadli qidiruvni amalga oshiradi.
   - Topilgan natijalar avtomatik ravishda **keshlanadi** (`search_cache`), bu esa keyingi foydalanuvchilar uchun qidiruv vaqtini deyarli 0 soniyaga tushiradi.
   - **Halollik prinsipi:** Agar internetda ham ishonchli material topilmasa, bot hech qachon to‘qima yoki sun’iy javob chiqarmaydi, balki *"Bu topshiriqning ishonchli javobi hozircha topilmadi"* deb ochiq xabar beradi.

5. **Zamonaviy Telegram interfeysi (UI/UX):**
   - 100% Inline tugmalar orqali ishlaydi.
   - Ko‘p fanli sinflar uchun qulay **sahifalash (pagination)** tizimi (`⬅️ Oldingi`, `Keyingi ➡️`).
   - Har bir bosqichda **`⬅️ Orqaga`** va **`🏠 Bosh menyu`** tugmalari mavjud.
   - Natija sahifasida **`🌐 Manbani ochish`**, **`🔄 Qayta qidirish`** va topilmaganda **`📩 Adminga buyurtma berish`** tugmalari bor.
   - Bir vaqtning o‘zida yuzlab o‘quvchilarga asinxron (`aiogram 3.x` va `aiosqlite`) xizmat ko‘rsatadi.

6. **Keng qamrovli Admin Paneli (`/admin`):**
   - **📊 Umumiy statistika:** Jami foydalanuvchilar, bugungi faollar, topshiriqlar soni, qidiruvlar va xatoliklar soni.
   - **➕ Topshiriq qo‘shish ustasi (Wizard):** Sinf, chorak, fan, tur, savollar, javoblar, manba va PDF/rasm biriktirish.
   - **🔍 Qidiruv xatolari & Talablar:** O‘quvchilar eng ko‘p qidirgan, lekin topilmagan fanlar va topshiriqlar tahlili.
   - **📚 Fanlar nazorati:** Sinflar bo‘yicha mavjud fanlarni ko‘rish.
   - **📢 Barchaga xabar yuborish (Broadcast):** Barcha ro‘yxatdan o‘tgan foydalanuvchilarga xabar tarqatish.

---

## 📁 Loyiha tuzilishi

```text
bsbchsbbot/
│
├── bot/
│   ├── __init__.py
│   ├── config.py             # Sozlamalar (.env dan BOT_TOKEN, ADMIN_IDS yuklash)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py             # SQLite asinxron ulanish va jadval sxemalari
│   │   ├── models.py         # CRUD amallari (foydalanuvchilar, fanlar, topshiriqlar, kesh)
│   │   └── seed_data.py      # O'zbekiston 5-11-sinf fanlari va namunaviy BSB/CHSB lar
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py          # /start, /help, /menu buyruqlari
│   │   ├── student.py        # O'quvchi ssenariysi (Sinf -> Chorak -> Fan -> BSB/CHSB -> Javob)
│   │   └── admin.py          # Admin boshqaruv paneli (/admin va FSM qo'shish)
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline.py         # O'quvchi inline tugmalari va sahifalash
│   │   └── admin_kb.py       # Admin boshqaruv klaviaturalari
│   ├── services/
│   │   ├── __init__.py
│   │   └── search_service.py # Internetdan qidirish, tahlil qilish va keshlash
│   └── utils/
│       ├── __init__.py
│       └── helpers.py        # Chiroyli matn formatlash va xatolik xabarlari
│
├── data/
│   └── bot.db                # SQLite ma'lumotlar bazasi
├── tests/
│   └── test_bot.py           # Loyihaning avtomatlashtirilgan testlari
├── .env.example              # Muhit o'zgaruvchilari namunasi
├── .env                      # Haqiqiy maxfiy kalitlar fayli
├── requirements.txt          # Python kutubxonalari ro'yxati
├── README.md                 # To'liq hujjat va ishga tushirish yo'riqnomasi
└── main.py                   # Botning asosiy kirish nuqtasi
```

---

## 🚀 Ishga tushirish bo‘yicha qo‘llanma

### 1-qadam: Kutubxonalarni o‘rnatish

Loyihani terminal yoki buyruqlar satrida oching va kerakli kutubxonalarni yuklang:

```bash
pip install -r requirements.txt
```

### 2-qadam: Bot tokeni va admin ID sini sozlash

Loyihaning asosiy papkasida `.env` nomli fayl yarating (yoki `.env.example` dan nusxa oling):

```ini
# Telegram @BotFather dan olingan bot tokeni
BOT_TOKEN=1234567890:AAHxxxxxx_your_bot_token_here

# Admin Telegram ID raqamlari (vergul bilan ajratilgan)
# O'z ID raqamingizni @userinfobot orqali bilib olishingiz mumkin
ADMIN_IDS=123456789

# Ma'lumotlar bazasi yo'li
DATABASE_PATH=data/bot.db

# Qidiruv sozlamalari
ENABLE_ONLINE_SEARCH=true
SEARCH_MAX_RESULTS=5
SEARCH_CACHE_DAYS=14
```

### 3-qadam: Botni ishga tushirish

Quyidagi buyruqni bering:

```bash
python main.py
```

Bot ishga tushishi bilan:
- Ma'lumotlar bazasi avtomatik yaratiladi va 5–11-sinf fanlari bilan to‘ldiriladi.
- Konsolda `>>> Bot ishlamoqda! Telegramdan @sizning_botingiz ga /start yuboring.` xabari ko‘rinadi.

---

## 🧪 Avtomatlashtirilgan testlarni tekshirish

Loyiha kodlarining to‘g‘riligini, har bir sinf fanlarining mustaqilligini va ma’lumotlar bazasi tizimini test qilish uchun quyidagi buyruqni ishga tushiring:

```bash
python -m unittest tests/test_bot.py
```

---

## 📱 Botdan foydalanish tartibi (User Flow)

1. Foydalanuvchi Telegramda **`/start`** buyrug‘ini yuboradi.
2. Bot: *"Assalomu alaykum! Sinfingizni tanlang"* degan xabar bilan **5-sinfdan 11-sinfgacha** tugmalarni chiqaradi.
3. Sinf tanlangach, **1, 2, 3 va 4-chorak** tugmalari ko‘rsatiladi.
4. Chorak tanlangach, aynan shu sinfga tegishli **haqiqiy o‘quv fanlari** sahifalangan holda chiqadi.
5. Fan tanlangach, **📝 BSB** yoki **📑 CHSB** tanlovi beriladi.
6. Tur tanlangach, topshiriq raqami (masalan: `1-BSB`, `2-BSB`, `CHSB 1-variant`...) ko‘rsatiladi.
7. Bot topshiriqni topib, quyidagi ma’lumotlarni ko‘rsatadi:
   - Sinf, Chorak, Fan nomi;
   - Topshiriq turi va raqami;
   - Topshiriq savollari;
   - Topilgan javoblar va yechimlar;
   - Ochiq manba havolasi (sayt yoki PDF yuklash havolasi);
8. Har qanday vaqtda **`⬅️ Orqaga`** yoki **`🏠 Bosh menyu`** orqali orqaga qaytish mumkin.
