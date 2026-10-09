# ✍️ AI Content Studio

Ko'p kanalli kontent yaratish, tahrirlash, qayta ishlash (Cross-Channel Repurposing) va eksport qilish uchun sun'iy intellekt platformasi (FastAPI + Async SQLite + Multi-Platform Engine).

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.en.md) | [Русский](README.ru.md) | [O'zbekcha](README.md)

---

## 🌟 Imkoniyatlar va Arxitektura

AI Content Studio — zamonaviy kontent ijodkorlari, marketologlar va jamoalar uchun yagona manbadan bir vaqtning o'zida barcha ommabop tarmoqlarga moslashtirilgan materiallar tayyorlovchi tizim:

- 📝 **SEO Blog & Maqolalar**: H1 sarlavhalar, meta-tavsiflar, mundarija, H2/H3 bo'limlar va CTA bilan to'liq maqolalar.
- 🧵 **X / Twitter Threads**: Diqqatni tortuvchi boshlang'ich hook, 4 qismli tvit zanjiri va tegishli heshteglar.
- 💼 **LinkedIn Postlari**: Professional tahlil, qisqa abzaslar, xulosalar va auditoriyani jalb qiluvchi savollar.
- 📸 **Instagram / Threads**: Vizual hikoyalar, emojilar bilan bezatilgan matn va alohida heshteg bloklari.
- ✈️ **Telegram Xabarlari**: Markdown formatidagi qalin matnlar, nuqtali ro'yxatlar va havolalar bilan boyitilgan xabarlar.
- 🎬 **Video Ssenariylari**: 60 soniyali YouTube Shorts / TikTok / Reels uchun sekundma-sekund vaqt belgilari (`[0-3s]`, `[3-15s]`, `[15-45s]`, `[45-60s]`) va kadr orti ko'rsatmalari (`[VISUAL: ...]`).
- 🔄 **Cross-Channel Repurposing (Qayta ishlash)**: Istalgan bitta maqola yoki matndan birgina API so'rovi orqali barcha 5 tarmoq uchun tayyor postlar to'plamini bir vaqtda generatsiya qilish.
- 📚 **Tahririyat va Versiyalash**: Loyihalar (Projects), kontent turlari, nashr holati (`draft`, `review`, `published`) va avtomatik versiyalar (Revisions) tarixi.
- 📤 **Ko'p Formatli Eksport**: Kontentni to'g'ridan-to'g'ri Markdown (`.md`), HTML (`.html`) yoki tizimli JSON formatlarida yuklab olish.
- 🔌 **Deterministik Offline Rejim**: Gemini API kaliti kiritilmaganda yoki internet uzilganda ham real, sifatli kontent generatsiya qiluvchi avtonom fallback mexanizmi.

---

## 🏗️ Arxitektura tuzilishi

```
src/content_studio/
├── __init__.py
├── config.py              # Pydantic v2 sozlamalari va muhit o'zgaruvchilari
├── app.py                 # FastAPI factory, lifespan, CORS va middleware
├── main.py                # Serverni ishga tushirish (CLI entrypoint)
├── models/
│   ├── project.py         # Project, ProjectCreate, ProjectUpdate
│   ├── content.py         # ContentItem, ContentType, ContentStatus, Tone, Revision
│   └── generation.py      # GenerateRequest, RepurposeRequest, ExportFormat
├── database/
│   └── repository.py      # aiosqlite orqali async SQLite ombori
├── engine/
│   ├── base.py            # BaseGenerator (Gemini API + deterministik fallback)
│   ├── blog_generator.py  # SEO Blog va maqola dvigateli
│   ├── social_generator.py# X, LinkedIn, Instagram, Telegram postlari
│   ├── video_script_generator.py # Shorts, Reels va YouTube ssenariylari
│   └── repurposer.py      # Ko'p kanalli qayta ishlash orkestratori
└── api/
    ├── dependencies.py    # FastAPI dependency injection
    ├── routes_projects.py # Loyihalar CRUD
    ├── routes_content.py  # Kontentlar boshqaruvi va versiyalash
    ├── routes_generator.py# /generate va /repurpose
    ├── routes_export.py   # Markdown, HTML, JSON eksporti
    └── routes_analytics.py# Tahliliy dashboard
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.10 yoki undan yuqori
- SQLite 3

### 2. Kutubxonalarni o'rnatish
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Konfiguratsiya
```bash
cp .env.example .env
```

Parametrlar tavsifi:
```env
APP_ENV=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///data/content_studio.db
GEMINI_API_KEY=               # Ixtiyoriy: agar kiritilmasa, offline intellekt ishlaydi
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Serverni ishga tushirish
```bash
python3 src/content_studio/main.py
```
Yoki Uvicorn orqali:
```bash
uvicorn content_studio.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

OpenAPI Swagger hujjati brauzerda: `http://localhost:8000/docs`

---

## 🐳 Docker orqali ishga tushirish

```bash
docker compose up -d --build
```

---

## 📡 Asosiy API Endpointlari

| Metod | Yo'l | Tavsif |
|---|---|---|
| `GET` | `/health` | Server va ma'lumotlar bazasi holati |
| `POST` | `/projects` | Yangi loyiha / kampaniya yaratish |
| `GET` | `/projects` | Barcha loyihalar ro'yxati |
| `POST` | `/content` | Qo'lda yangi kontent kiritish |
| `GET` | `/content?project_id=1&content_type=blog` | Kontentlarni filtrlash va qidirish |
| `PATCH` | `/content/{id}` | Kontentni tahrirlash (yangi versiya yaratadi) |
| `GET` | `/content/{id}/revisions` | Kontent tahrirlar tarixi |
| `POST` | `/generator/generate` | AI orqali ma'lum kanal uchun kontent yaratish |
| `POST` | `/generator/repurpose` | Matnni barcha tarmoqlarga moslashtirish |
| `GET` | `/export/{id}?format=markdown` | Markdown, HTML yoki JSON shaklida eksport |
| `GET` | `/analytics/summary?project_id=1` | Loyiha statistikasi va so'zlar soni |

### Cross-Channel Repurpose so'rovi namunasi:
```bash
curl -X POST "http://localhost:8000/generator/repurpose?save_to_project_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Building scalable microservices with FastAPI and async SQLite. Emphasizing clean architecture, fault tolerance, and comprehensive automated testing.",
    "tone": "conversational"
  }'
```

---

## 🧪 Avtomatlashtirilgan Testlar

Loyiha to'liq Pytest va Pytest-Asyncio bilan qamrab olingan:

```bash
PYTHONPATH=src pytest -v tests/
```

- `tests/test_config.py` — Konfiguratsiya va yo'llar
- `tests/test_database.py` — Loyihalar, kontent, versiyalash va analitika
- `tests/test_generators.py` — Blog, ijtimoiy tarmoqlar va video ssenariylar
- `tests/test_repurposer.py` — Ko'p kanalli qayta ishlash dvigateli
- `tests/test_export.py` — Markdown, HTML va JSON eksport turlari
- `tests/test_api.py` — Barcha REST API yo'nalishlari va chekka holatlar

---

## 📄 Litsenziya

MIT License © 2026 [Afzalbek](https://github.com/afzalbek-dev).
