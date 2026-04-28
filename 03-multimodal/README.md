# AI Finance Advisor Bot (MVP)

Минимальный Telegram-бот для учета личных доходов и расходов на базе LLM/VLM.

## Что умеет

- Обрабатывает текстовые сообщения о доходах и расходах
- Обрабатывает фото чеков через визуальную модель
- Извлекает данные в structured output и сохраняет in-memory
- Ведет журнал транзакций per-user без БД
- По запросу дает отчет: баланс за период + категории
- Корректно обрабатывает ошибки LLM/VLM и неподходящий ввод

## Технологии

- Python 3.12, uv
- aiogram 3 (Telegram Bot API, polling)
- openai client → OpenRouter или Ollama
- Docker + docker compose
- ruff, pytest

## Быстрый старт

### 1. Переменные окружения

Скопируй `.env.example` в `.env` и заполни:

| Переменная | Обязательная | Описание |
|------------|:---:|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен бота от @BotFather |
| `LLM_API_KEY` | ✅* | API-ключ провайдера моделей (`*` для Ollama может не требоваться) |
| `LLM_BASE_URL` | | `https://openrouter.ai/api/v1` или локальный URL Ollama |
| `LLM_TEXT_MODEL` | | Текстовая модель для structured extraction |
| `LLM_VISION_MODEL` | | Визуальная модель для обработки чеков |
| `SYSTEM_PROMPT` | | Роль/поведение финансового ассистента |
| `DIALOG_HISTORY_LIMIT` | | Кол-во сообщений в памяти (дефолт 10) |
| `LLM_TIMEOUT_SECONDS` | | Таймаут запроса к модели в секундах (дефолт 30) |
| `LLM_MAX_RETRIES` | | Кол-во повторов при временной ошибке (дефолт 2) |
| `MAX_RECEIPT_IMAGE_BYTES` | | Максимальный размер фото чека в байтах |
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

## Примеры сообщений

- Текстовый расход: `Сегодня в 14:20 потратил 1250 на продукты в Пятерочке`
- Текстовый доход: `Вчера получил 50000 зарплату`
- Отчет: `Покажи отчет за месяц`
- Чек: отправь фото чека как изображение в чат

## Сквозная проверка MVP

1. Запусти бота (`make run`) и отправь `/start`.
2. Отправь текст о доходе и дождись подтверждения сохранения.
3. Отправь текст о расходе и дождись подтверждения сохранения.
4. Отправь фото чека и дождись подтверждения сохранения.
5. Запроси отчет за месяц и проверь доходы, расходы, баланс и категории.

## Структура проекта

```
src/
  config.py          # Settings из переменных окружения
  logger.py          # настройка logging
  main.py            # точка входа
  llm_client.py      # запросы к LLM/VLM через openai client
  chat_service.py    # оркестрация: извлечение + отчеты
  dialog_history.py  # in-memory буфер диалога per-user
  transaction.py     # модель финансовой транзакции
  transaction_store.py # in-memory журнал транзакций per-user
  handlers/
    start.py         # /start
    message.py       # текст и фото
tests/
docs/
```

## Документация

- `docs/idea.md` — концепция
- `docs/vision.md` — техническое видение
- `docs/tasklist.md` — план итераций
