# Telegram LLM Bot (MVP)

Telegram-бот на **aiogram 3** с диалогом через **OpenRouter** (OpenAI-совместимый API). История сообщений хранится в памяти процесса.

## Возможности

- Команда `/start` — приветствие без сброса истории
- Текстовый диалог с учётом системного промпта и последних N пар сообщений
- Только личные чаты (`private`)
- Обработка нетекстового ввода, пустых сообщений и ошибок LLM

## Технологии

Python 3.12, **uv**, **Makefile**, aiogram 3 (long polling), `openai` (AsyncOpenAI → OpenRouter), pydantic-settings, ruff. Опционально Docker Compose.

## Переменные окружения

Скопируйте **`.env.example`** в **`.env`** и заполните обязательные поля:

| Переменная | Обязательная | Описание |
|------------|:------------:|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен от @BotFather |
| `OPENROUTER_API_KEY` | ✅ | API-ключ OpenRouter |
| `LLM_MODEL` | ✅ | Идентификатор модели |
| `SYSTEM_PROMPT` | ✅ | Системный промпт / роль ассистента |
| `OPENROUTER_BASE_URL` | | По умолчанию `https://openrouter.ai/api/v1` |
| `HISTORY_MAX_PAIRS` | | Лимит пар user/assistant, по умолчанию `10` |
| `LLM_TIMEOUT_SEC` | | Таймаут запроса к LLM, по умолчанию `60` |
| `LOG_LEVEL` | | Например `INFO`, `DEBUG` |
| `OPENROUTER_HTTP_REFERER` | | Опциональный заголовок OpenRouter |
| `OPENROUTER_X_TITLE` | | Опциональный заголовок OpenRouter |

## Запуск

### Локально

```bash
make install   # uv sync --dev
make run       # uv run python -m app
```

### Проверки

```bash
make lint      # ruff check + format
make check     # self-check: история, слои, интеграция с OpenRouter
```

### Docker

```bash
make docker-build
make docker-run
# или
make up        # docker compose up -d --build
make down
```

Нужен **`.env`** в корне проекта (как при локальном запуске).

## Деплой (systemd)

Пример unit-файла `/etc/systemd/system/telegram-llm-bot.service`:

```ini
[Unit]
Description=Telegram LLM Bot
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

Команды:

```bash
sudo systemctl enable --now telegram-llm-bot
sudo journalctl -u telegram-llm-bot -f
```

Альтернатива без Compose: `docker run --env-file .env --restart unless-stopped telegram-llm-bot`.

## Структура `app/`

- `main.py` — composition root, сборка зависимостей, запуск polling
- `config/settings.py` — `Settings` и валидация env
- `bot/telegram_bot.py` — Bot, Dispatcher, long polling
- `handlers/message_handler.py` — `/start`, текст, граничные случаи
- `services/dialog_service.py` — сборка messages, вызов LLM
- `services/chat_history.py` — история в RAM по `chat_id`
- `llm/openrouter_client.py` — клиент OpenRouter
- `rag/context_provider.py` — заглушка для будущего RAG

## Документация

- `docs/vision.md` — техническое видение
- `docs/tasklist.md` — итерации и чеклисты
