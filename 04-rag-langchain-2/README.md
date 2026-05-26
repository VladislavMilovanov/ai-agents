# Telegram RAG-бот (продукты Сбера)

Telegram-бот на **aiogram 3** и **LangChain**: диалог с памятью, ответы через **OpenRouter** (LLM + эмбеддинги), **RAG** по локальному корпусу в **`InMemoryVectorStore`**.

## Возможности

- Ответы по документам из `data/` (PDF + JSON), с **query transformation** и учётом истории
- **Переиндексация** при старте и по команде `/index`
- **`/index_status`** — число чанков в индексе
- Команда `/start` — приветствие (история не сбрасывается)
- Только личные чаты (`private`)

## Корпус `data/`

| Файл | Описание |
|------|----------|
| `ouk_potrebitelskiy_kredit_lph.pdf` | Потребительский кредит |
| `usl_r_vkladov.pdf` | Вклады |
| `sberbank_help_documents.json` | Справка (FAQ) |

Файлы должны быть валидными (настоящие PDF). После замены корпуса — `/index`.

## Переменные окружения

Скопируйте **`.env.example`** → **`.env`** и заполните секреты.

| Переменная | Обязательная | Описание |
|------------|:------------:|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен @BotFather |
| `OPENROUTER_API_KEY` | ✅ | Ключ OpenRouter |
| `LLM_MODEL` | ✅ | Модель чата |
| `EMBEDDING_MODEL` | ✅ | Модель эмбеддингов |
| `RETRIEVER_K` | ✅ | Топ-K чанков (≥ 1) |
| `SYSTEM_PROMPT` | | Роль ассистента Сбера (есть дефолт в коде) |
| `OPENROUTER_BASE_URL` | | `https://openrouter.ai/api/v1` |
| `DATA_DIR` | | Папка корпуса, default `data` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | | Параметры сплиттера |
| `HISTORY_MAX_PAIRS` | | Лимит пар в истории, default `10` |
| `LLM_TIMEOUT_SEC` | | Таймаут LLM, default `60` |
| `LOG_LEVEL` | | `INFO`, `DEBUG`, … |

## Запуск

```bash
make install    # uv sync --dev
make run        # индексация при старте + polling
```

Первый старт может занять время (эмбеддинги всего корпуса).

### Проверки

```bash
make lint       # ruff
make test       # pytest
make check      # локальный self-check (слои без сети)
```

### Docker

```bash
make docker-build
make docker-run
# или
make up
make down
```

В образ копируются `app/` и **`data/`**. Нужен `.env` в корне.

## Команды в Telegram

| Команда | Действие |
|---------|----------|
| `/start` | Приветствие |
| `/index` | Полная переиндексация |
| `/index_status` | Число чанков |
| Текст | Вопрос по RAG |

## Структура `app/`

- `main.py` — DI, индексация при старте, polling
- `config/settings.py` — конфигурация
- `handlers/` — сообщения и команды индекса
- `services/dialog_service.py` — диалог → `RagChain`
- `services/chat_history.py` — история (`HumanMessage` / `AIMessage`)
- `rag/corpus_loader.py`, `index_service.py`, `rag_chain.py` — RAG

## Деплой (systemd)

```ini
[Unit]
Description=Telegram RAG Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/telegram-llm-bot
ExecStart=/usr/bin/docker compose up -d --build
ExecStop=/usr/bin/docker compose down
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now telegram-llm-bot
sudo journalctl -u telegram-llm-bot -f
```

## Документация

- [docs/idea.md](docs/idea.md) — идея продукта
- [docs/vision.md](docs/vision.md) — архитектура и требования
- [docs/tasklist.md](docs/tasklist.md) — план итераций

Референс пайплайна: `naive-rag.ipynb` / цепочка `rag_query_transform_chain`.
