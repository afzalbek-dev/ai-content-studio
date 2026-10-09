# ✍️ AI Content Studio

Платформа генерации цифрового контента, кросс-канальной адаптации (Repurposing) и редакционной работы на базе Python, FastAPI и Async SQLite.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.en.md) | [Русский](README.ru.md) | [O'zbekcha](README.md)

---

## 🌟 Возможности и Архитектура

AI Content Studio позволяет авторам, маркетологам и разработчикам из одного исходного текста создавать комплекс материалов, оптимизированных для всех ключевых платформ:

- 📝 **SEO Блог и Статьи**: Заголовки H1, мета-описания, оглавление, структурированные разделы H2/H3 с примерами и призывами к действию.
- 🧵 **Треды для X / Twitter**: Цепляющий хук, цепочка из 4 твитов (`🧵 1/4`, `2/4`) и релевантные хэштеги.
- 💼 **Публикации для LinkedIn**: Профессиональный тон, структурированные абзацы, выводы и вовлекающие вопросы.
- 📸 **Instagram / Threads**: Визуальный сторителлинг, эмодзи-разметка, призывы сохранить пост и хэштеги.
- ✈️ **Сообщения для Telegram**: Богатая Markdown-разметка с жирными заголовками, списками и ссылками.
- 🎬 **Сценарии для видео**: 60-секундные таймкоды для Shorts / Reels / TikTok (`[0-3s]`, `[3-15s]`, `[15-45s]`, `[45-60s]`) с подсказками для оператора и монтажера (`[VISUAL: ...]`).
- 🔄 **Кросс-канальный реперпозинг (Repurposing)**: За один API-запрос преобразует статью, транскрипт или заметку во все 5 форматов одновременно.
- 📚 **Редакционный центр и ревизии**: Управление проектами/кампаниями, жизненный цикл (`draft`, `review`, `published`) и версионирование изменений.
- 📤 **Мультиформатный экспорт**: Выгрузка материалов в чистый Markdown (`.md`), автономный адаптивный HTML (`.html`) или структурированный JSON.
- 🔌 **Автономный офлайн-режим**: Встроенный детерминированный движок обеспечивает генерацию качественных материалов даже без интернета и API ключей.

---

## 🏗️ Структура Проекта

```
src/content_studio/
├── __init__.py
├── config.py              # Настройки Pydantic v2 и переменные окружения
├── app.py                 # Фабрика приложения FastAPI, lifespan и CORS
├── main.py                # Точка входа для Uvicorn
├── models/
│   ├── project.py         # Схемы проектов и кампаний
│   ├── content.py         # Схемы элементов контента, статусов и ревизий
│   └── generation.py      # Схемы запросов генерации, реперпозинга и экспорта
├── database/
│   └── repository.py      # Асинхронный репозиторий SQLite через aiosqlite
├── engine/
│   ├── base.py            # Базовый генератор с поддержкой Gemini и fallback
│   ├── blog_generator.py  # Генератор SEO-статей
│   ├── social_generator.py# Генератор для X, LinkedIn, Instagram, Telegram
│   ├── video_script_generator.py # Сценарии для Shorts, Reels и YouTube
│   └── repurposer.py      # Оркестратор кросс-канальной адаптации
└── api/
    ├── dependencies.py    # Провайдеры внедрения зависимостей FastAPI
    ├── routes_projects.py # CRUD проектов
    ├── routes_content.py  # Управление контентом и ревизиями
    ├── routes_generator.py# Эндпоинты /generate и /repurpose
    ├── routes_export.py   # Экспорт в Markdown, HTML и JSON
    └── routes_analytics.py# Аналитический дашборд
```

---

## 🚀 Быстрый Старт

### 1. Требования
- Python 3.10 или выше
- SQLite 3

### 2. Установка зависимостей
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Конфигурация окружения
Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

Параметры:
```env
APP_ENV=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///data/content_studio.db
GEMINI_API_KEY=               # Опционально: без ключа работает офлайн-генератор
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Запуск сервера
```bash
python3 src/content_studio/main.py
```
Или через Uvicorn:
```bash
uvicorn content_studio.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

Интерактивная документация Swagger UI: `http://localhost:8000/docs`.

---

## 🐳 Развертывание в Docker

```bash
docker compose up -d --build
```

---

## 📡 Справочник API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/health` | Проверка здоровья сервиса и БД |
| `POST` | `/projects` | Создать проект или кампанию |
| `GET` | `/projects` | Список проектов |
| `POST` | `/content` | Создать материал вручную |
| `GET` | `/content?project_id=1&content_type=blog` | Поиск и фильтрация контента |
| `PATCH` | `/content/{id}` | Редактировать контент (создает новую ревизию) |
| `GET` | `/content/{id}/revisions` | Просмотреть историю изменений |
| `POST` | `/generator/generate` | Сгенерировать контент для конкретной платформы |
| `POST` | `/generator/repurpose` | Адаптировать материал под все каналы |
| `GET` | `/export/{id}?format=markdown` | Экспорт в Markdown, HTML или JSON |
| `GET` | `/analytics/summary?project_id=1` | Статистика по объему и распределению по каналам |

---

## 🧪 Тестирование

Комплексный автоматизированный набор тестов Pytest:

```bash
PYTHONPATH=src pytest -v tests/
```

- `tests/test_config.py` — Валидация конфигурации и путей
- `tests/test_database.py` — CRUD проектов, материалов, ревизий и аналитики
- `tests/test_generators.py` — Генераторы для блога, соцсетей и видео-сценариев
- `tests/test_repurposer.py` — Кросс-канальный реперпозинг
- `tests/test_export.py` — Проверка форматов экспорта
- `tests/test_api.py` — Интеграционные тесты REST API

---

## 📄 Лицензия

MIT License © 2026 [Afzalbek](https://github.com/afzalbek-dev).
