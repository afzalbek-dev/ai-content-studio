# ✍️ AI Content Studio

Open-source AI-powered Content Creation, Cross-Channel Repurposing, and Editorial Studio built with Python, FastAPI, and Async SQLite.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.en.md) | [Русский](README.ru.md) | [O'zbekcha](README.md)

---

## 🌟 Features & Architecture

AI Content Studio empowers creators, marketing teams, and developers to generate, manage, and repurpose digital content across all major channels from a single source:

- 📝 **SEO Blog & Articles**: Generates H1 titles, meta descriptions, table of contents, structured H2/H3 body sections, and call-to-actions.
- 🧵 **X / Twitter Threads**: High-retention hooks, 4-part threaded breakdowns (`🧵 1/4`, `2/4`), and platform hashtags.
- 💼 **LinkedIn Insights**: Professional framing, short paragraph line breaks, key takeaways, and engagement prompts.
- 📸 **Instagram / Threads**: Visual storytelling, emoji accents, save CTAs, and clean hashtag blocks.
- ✈️ **Telegram Announcements**: Rich Markdown formatting with bold headers, bulleted points, and actionable links.
- 🎬 **Video Script Engine**: 60-second YouTube Shorts / TikTok / Reels scripts with exact timestamp checkpoints (`[0-3s]`, `[3-15s]`, `[15-45s]`, `[45-60s]`) and on-screen visual prompts (`[VISUAL: ...]`).
- 🔄 **Cross-Channel Repurposing**: In a single API call, transforms any article, transcript, or raw idea into a complete suite of platform-tailored deliverables.
- 📚 **Editorial Hub & Revisions**: Project campaigns, status lifecycles (`draft`, `review`, `published`), and automatic revision history tracking.
- 📤 **Multi-Format Export**: Instantly export content to clean Markdown (`.md`), standalone responsive HTML (`.html`), or structured JSON.
- 🔌 **Deterministic Offline Fallback**: Features a built-in deterministic intelligence engine that guarantees formatted deliverables even without API keys or internet access.

---

## 🏗️ Project Architecture

```
src/content_studio/
├── __init__.py
├── config.py              # Pydantic v2 settings & environment variables
├── app.py                 # FastAPI application factory, lifespan & CORS
├── main.py                # Server entrypoint launcher
├── models/
│   ├── project.py         # Project schemas & validation
│   ├── content.py         # ContentItem, ContentType, Status & Revision schemas
│   └── generation.py      # Generation, Repurposing & Export schemas
├── database/
│   └── repository.py      # Async SQLite repository via aiosqlite
├── engine/
│   ├── base.py            # BaseGenerator with Gemini integration & fallback
│   ├── blog_generator.py  # SEO article generator
│   ├── social_generator.py# X, LinkedIn, Instagram, Telegram engines
│   ├── video_script_generator.py # Shorts, Reels & video scripts
│   └── repurposer.py      # Cross-channel repurposing orchestrator
└── api/
    ├── dependencies.py    # FastAPI dependency providers
    ├── routes_projects.py # Projects CRUD
    ├── routes_content.py  # Content management & revisions
    ├── routes_generator.py# /generate and /repurpose endpoints
    ├── routes_export.py   # Markdown, HTML, and JSON export
    └── routes_analytics.py# Studio metrics dashboard
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- SQLite 3

### 2. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configuration parameters:
```env
APP_ENV=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///data/content_studio.db
GEMINI_API_KEY=               # Optional: Uses deterministic offline generator if empty
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Running the Server
```bash
python3 src/content_studio/main.py
```
Or via Uvicorn:
```bash
uvicorn content_studio.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

---

## 🐳 Docker Deployment

```bash
docker compose up -d --build
```

---

## 📡 API Endpoints Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health status & DB connectivity |
| `POST` | `/projects` | Create new campaign or project |
| `GET` | `/projects` | List all projects |
| `POST` | `/content` | Create content item manually |
| `GET` | `/content?project_id=1&content_type=blog` | Filter and search content items |
| `PATCH` | `/content/{id}` | Update content item (records revision) |
| `GET` | `/content/{id}/revisions` | View edit revision history |
| `POST` | `/generator/generate` | Generate channel-tailored AI content |
| `POST` | `/generator/repurpose` | Cross-channel repurposing into all formats |
| `GET` | `/export/{id}?format=markdown` | Export as Markdown, HTML, or JSON |
| `GET` | `/analytics/summary?project_id=1` | Get content count, word counts, and distribution |

### Example Repurposing Request:
```bash
curl -X POST "http://localhost:8000/generator/repurpose?save_to_project_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Building scalable microservices with FastAPI and async SQLite. Emphasizing clean architecture, fault tolerance, and comprehensive automated testing.",
    "tone": "conversational"
  }'
```

---

## 🧪 Testing

The repository includes a comprehensive automated test suite powered by Pytest:

```bash
PYTHONPATH=src pytest -v tests/
```

Test coverage includes:
- `tests/test_config.py` — Settings validation & directory paths
- `tests/test_database.py` — Projects, content items, revisions & analytics
- `tests/test_generators.py` — Blog, social channels & video script structures
- `tests/test_repurposer.py` — Full & targeted cross-channel repurposing
- `tests/test_export.py` — Markdown, HTML & JSON exports
- `tests/test_api.py` — REST API integration & edge cases

---

## 📄 License

MIT License © 2026 [Afzalbek](https://github.com/afzalbek-dev).
