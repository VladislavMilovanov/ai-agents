# AI Telegram Assistant (MVP)

Минимальный Telegram-бот с LLM-ответами через OpenRouter.

## Что умеет

- Отвечает на текстовые сообщения через LLM
- Помнит последние реплики диалога (per-user, in-memory)
- Работает с заданной ролью через системный промпт
- Корректно обрабатывает ошибки LLM и нетекстовый ввод

## Технологии

- Python 3.12, uv
- aiogram 3 (Telegram Bot API, polling)
- openai client → OpenRouter
- Docker + docker compose
- ruff, pytest

## Быстрый старт

### 1. Переменные окружения

Скопируй `.env.example` в `.env` и заполни:

| Переменная | Обязательная | Описание |
|------------|:---:|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен бота от @BotFather |
| `OPENROUTER_API_KEY` | ✅ | API-ключ OpenRouter |
| `OPENROUTER_BASE_URL` | | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | | Модель, например `openrouter/auto` |
| `SYSTEM_PROMPT` | | Роль/поведение ассистента |
| `DIALOG_HISTORY_LIMIT` | | Кол-во сообщений в памяти (дефолт 10) |
| `LOG_LEVEL` | | `INFO` или `DEBUG` |

### 2. Нативный запуск

```bash
make install   # установить зависимости
make run       # запустить бота
```

### 3. Запуск в Docker

```bash
make docker-build  # собрать образ
make docker-run    # запустить через compose
make docker-stop   # остановить
```

## Проверки

```bash
make lint   # ruff
make test   # pytest
```

## Структура проекта

```
src/
  config.py          # Settings из переменных окружения
  logger.py          # настройка logging
  main.py            # точка входа
  llm_client.py      # запросы к OpenRouter
  chat_service.py    # оркестрация: история + LLM
  dialog_history.py  # in-memory буфер диалога per-user
  handlers/
    start.py         # /start
    message.py       # текстовые сообщения
tests/
docs/
```

## Документация

- `docs/idea.md` — концепция
- `docs/vision.md` — техническое видение
- `docs/tasklist.md` — план итераций
