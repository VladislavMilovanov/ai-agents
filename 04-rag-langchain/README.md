# AI Telegram RAG-бот (MVP)

Telegram-бот на **aiogram** и **LangChain**: диалог с памятью, ответы через **OpenRouter** (LLM + эмбеддинги), **RAG** по локальному корпусу в **`InMemoryVectorStore`**.

## Возможности

- Текстовый диалог с учётом последних реплик (**LangChain** `HumanMessage` / `AIMessage`, in-memory per-user).
- Если индекс не пустой: **query transformation** → **семантический поиск** (топ-**K**, **`RETRIEVER_K`**) → ответ с опорой на чанки.
- Если индекс пустой: обычный запрос к LLM без RAG.
- Команды **`/index`** (полная переиндексация) и **`/index_status`** (число чанков); состояние диалога они не затрагивают.
- Ошибки API и нетекстовый ввод обрабатываются без падения процесса.

## Технологии

Python 3.12, **uv**, **Makefile**, aiogram 3 (polling), LangChain, `openai`-клиент к OpenRouter, ruff, pytest. Опционально Docker Compose.

## Корпус в `data/`

Положите файлы в каталог **`data/`** в корне проекта (или в путь из **`DATA_DIR`**):

- `ouk_potrebitelskiy_kredit_lph.pdf`
- `usl_r_vkladov.pdf`
- `sberbank_help_documents.json`

Отсутствующие файлы пропускаются с предупреждением в логах. После смены файлов выполните **`/index`** или перезапустите бота (при старте индексация тоже выполняется).

## Переменные окружения

Скопируй **`.env.example`** в **`.env`**. При старте **`Settings`** проверяет обязательные параметры и разумные диапазоны (ключ OpenRouter не пустой, **`RETRIEVER_K` ≥ 1**, **`CHUNK_OVERLAP` < `CHUNK_SIZE`**, базовый URL начинается с `http`).

| Переменная | Обязательная | Описание |
|------------|:---:|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен от @BotFather |
| `OPENROUTER_API_KEY` | ✅ | Ключ OpenRouter (не пустой) |
| `OPENROUTER_BASE_URL` | | По умолчанию `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | ✅* | Модель чата (*непустая строка, есть дефолт) |
| `EMBEDDING_MODEL` | ✅* | Модель эмбеддингов (*дефолт в примере) |
| `RETRIEVER_K` | | Целое ≥ 1, по умолчанию `4` |
| `DATA_DIR` | | Каталог корпуса относительно корня проекта, по умолчанию `data` |
| `CHUNK_SIZE` | | ≥ 100, по умолчанию `1000` |
| `CHUNK_OVERLAP` | | Неотрицательное, строго меньше `CHUNK_SIZE`, по умолчанию `200` |
| `DIALOG_HISTORY_LIMIT` | | ≥ 1, по умолчанию `10` |
| `SYSTEM_PROMPT` | | Необязательно; иначе роль из `config.py` |
| `LOG_LEVEL` | | Например `INFO`, `DEBUG` |

## Запуск

### Локально

```bash
make install   # uv sync
make run       # uv run python -m src.main
```

### Docker

В **docker-compose** смонтирован том `./data:/app/data`, чтобы корпус совпадал с локальным.

```bash
make docker-build
make docker-run
make docker-stop
```

Нужен **`.env`** в корне проекта (как при локальном запуске).

## Проверки

```bash
make lint   # ruff
make test   # pytest (моки эмбеддингов/LLM, без реальных вызовов API)
```

## Команды бота

| Команда | Действие |
|---------|----------|
| `/start` | Приветствие |
| `/index` | Пересобрать индекс из `data/` |
| `/index_status` | Показать число чанков (или сообщение, если индекс пуст) |

## Структура `src/`

- `main.py` — точка входа, индексация при старте
- `config.py` — `Settings` и валидация
- `index_service.py`, `corpus_loader.py` — загрузка и чанки
- `rag_chain.py` — RAG-цепочка
- `chat_service.py`, `dialog_history.py`, `llm_client.py`
- `handlers/` — Telegram-команды и сообщения

## Документация

- `docs/vision.md` — техническое видение
- `docs/tasklist.md` — итерации и чеклисты
