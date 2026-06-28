# 🎵 Audio Bot — Telegram musiqa va video yuklab beruvchi bot

## Imkoniyatlar

- 🎧 Qo'shiq nomi bo'yicha qidirish va MP3 yuklab berish (YouTube orqali)
- 🔗 TikTok / Instagram / YouTube / Pinterest havolasidan video yuklab berish (720p)
- 🎙 Ovozli xabar/audio yuborilsa, qo'shiqni aniqlash (Shazam uslubida)
- 🎬 Yuklangan videodan ovozni alohida ajratib olish
- 📁 Pleylistlar (qo'shiqlarni saqlash)
- 🔥 `/top` — kunlik/haftalik eng ko'p so'ralgan qo'shiqlar
- 🌐 3 tilda interfeys: o'zbek, rus, ingliz
- ⚡ Keshlash — bir marta yuklangan qo'shiq qayta yuklanmaydi, darhol yuboriladi
- 🔍 Inline qidiruv (`@botim qo'shiq nomi` — boshqa chatlarda ham)

## Loyiha tuzilmasi

```
music_bot/
├── main.py                  # bot ishga tushadigan asosiy fayl
├── config.py                # sozlamalar (.env dan o'qiydi)
├── database.py               # SQLite - userlar, kesh, trend, pleylist
├── locales.py                 # uz/ru/en tarjimalar
├── keyboards.py              # inline tugmalar
├── handlers/
│   ├── start.py               # /start, til tanlash
│   ├── search.py             # matnni link/qidiruvga ajratish
│   ├── music.py               # qo'shiq qidirish va yuborish
│   ├── video.py               # video yuklash + audio ajratish
│   ├── recognize.py          # ovozdan qo'shiq aniqlash
│   ├── inline.py              # inline qidiruv
│   ├── playlist.py            # pleylistlar
│   └── trending.py           # /top
├── utils/
│   ├── downloader.py          # yt-dlp wrapper (audio/video yuklash)
│   └── recognizer.py         # shazamio wrapper
├── requirements.txt
├── Dockerfile                # ffmpeg + python (Render uchun MUHIM)
├── render.yaml
└── .github/workflows/keep_alive.yml   # 24/7 uyqudan uyg'otish
```

## 1-qadam: Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather)ga yozing
2. `/newbot` buyrug'i bilan bot yarating, **tokenni saqlab qo'ying**
3. Inline rejimni yoqish: `/setinline` → botingizni tanlang → placeholder matn kiriting (masalan: "Qo'shiq nomini yozing...")
4. (Ixtiyoriy) `/setprivacy` → Disable — agar bot guruhlarda barcha xabarlarni ko'rishi kerak bo'lsa

## 2-qadam: Lokal test qilish

```bash
cd music_bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# ffmpeg o'rnatilganligini tekshiring:
ffmpeg -version
# Yo'q bo'lsa: sudo apt install ffmpeg  (Linux)  /  brew install ffmpeg (Mac)

cp .env.example .env
# .env faylini ochib BOT_TOKEN ni kiriting

python main.py
```

## 3-qadam: GitHub'ga yuklash

```bash
git init
git add .
git commit -m "Audio bot - birinchi versiya"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/music-bot.git
git push -u origin main
```

## 4-qadam: Render'ga deploy qilish (bepul tarif)

1. [render.com](https://render.com) ga GitHub orqali kiring
2. **New → Web Service** → repo'ingizni tanlang
3. **Environment: Docker** ni tanlang (oddiy "Python" emas — chunki ffmpeg kerak!)
4. Environment Variables qo'shing:
   - `BOT_TOKEN` = botingiz tokeni
   - `ADMIN_ID` = sizning Telegram ID'ingiz (ixtiyoriy)
5. **Create Web Service** tugmasini bosing — bir necha daqiqada deploy bo'ladi

## 5-qadam: 24/7 ishlashi uchun (bepul tarifda "uyg'otish")

Render'ning bepul tarifi 15 daqiqa faolsizlikdan keyin "uxlab qoladi". Buni oldini olish uchun GitHub Actions orqali har 5 daqiqada ping yuboramiz:

1. `.github/workflows/keep_alive.yml` faylida `SIZNING-APP-NOMINGIZ.onrender.com` qismini Render bergan haqiqiy URL'ga almashtiring
2. GitHub repo → **Settings → Actions → General** → "Allow all actions" yoqilganligiga ishonch hosil qiling
3. Bu workflow avtomatik har 5 daqiqada ishga tushadi va botni uyg'otib turadi

> ⚠️ **Eslatma:** GitHub Actions bepul cron jadvali ba'zan 5-15 daqiqa kechikishi mumkin (GitHub'ning o'zi shunday ishlaydi, sizning xatoyingiz emas). Agar 100% barqaror kerak bo'lsa, [cron-job.org](https://cron-job.org) yoki [UptimeRobot](https://uptimerobot.com) kabi bepul tashqi xizmatlardan foydalaning — ular aniqroq vaqtda ping yuboradi.

## Bilishingiz kerak bo'lgan cheklovlar (MVP versiyasi)

| Masala | Izoh |
|---|---|
| Video keshi RAM'da | Bot qayta ishga tushganda "Ovoz ajratish" tugmasi ishlamay qoladi (fayl yo'q bo'ladi). Productionga chiqarishdan oldin buni Redis yoki diskdagi fayl + TTL bilan almashtiring. |
| Telegram fayl limiti | Oddiy Bot API orqali 50MB'gacha fayl yuborish mumkin. Uzunroq videolar uchun Local Bot API Server kerak bo'ladi. |
| Inline qidiruv | Faqat avval kamida bir marta so'ralgan (keshga tushgan) qo'shiqlar ko'rinadi — Telegram inline natijalari darhol qaytishi shart, shu sababli real vaqtda yuklab bo'lmaydi. |
| TikTok/Instagram extractorlari | yt-dlp ushbu platformalarning ichki API'siga tayanadi, ular vaqti-vaqti bilan o'zgaradi. Muammo chiqsa: `pip install -U yt-dlp` bilan yangilang. |
| shazamio | Norasmiy kutubxona, Shazam o'z API'sini o'zgartirsa ishlamay qolishi mumkin. Muqobil: [AudD.io](https://audd.io) rasmiy API'si (bepul limit bilan). |
| Mualliflik huquqi | Musiqa/video yuklab berish ko'p mamlakatlarda himoyalangan kontent masalasiga tegishi mumkin. Shaxsiy foydalanish uchun tool sifatida ishlatish tavsiya etiladi, ommaviy tarqatish uchun emas. |

## Keyingi rivojlanish g'oyalari

- Sifat tanlash tugmalarini (`keyboards.quality_keyboard`) `music.py`ga ulash (hozir kod tayyor, lekin handlerga bog'lanmagan)
- Pleylistni ko'rish/o'chirish/qo'shiqlarni ro'yxat qilish uchun to'liq CRUD
- Reklama/sponsorlik xabarlarini `/start` xabariga yoki har N-so'rovda ko'rsatish
- PostgreSQL'ga o'tish (Render'ning bepul SQLite fayl tizimi qayta deploy qilinganda tozalanadi!)

## requirements.txt versiyalari haqida

Kutubxona versiyalari (`aiogram`, `shazamio`, `yt-dlp`) vaqt o'tishi bilan yangilanadi. Agar `pip install` xato bersa, versiya raqamlarini olib tashlab (`pip install aiogram aiohttp aiosqlite yt-dlp shazamio python-dotenv`) eng so'nggi versiyalarni o'rnating.
