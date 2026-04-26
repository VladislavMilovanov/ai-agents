# AI Telegram Assistant (MVP)

Минимальный Telegram-бот с LLM-ответами для проверки идеи.

## Что делает проект

- Принимает текстовые сообщения в Telegram.
- Отправляет запрос в LLM через OpenRouter.
- Возвращает ответ пользователю в чат.

## Технологии

- Python 3.12
- uv (зависимости и запуск)
- aiogram (Telegram Bot API, polling)
- openai client (доступ к моделям через OpenRouter)
- Docker + docker compose
- Makefile (единая точка запуска команд)

## Требования

- Python 3.12+
- uv
- Docker и docker compose (для контейнерного запуска)
- Telegram Bot Token
- OpenRouter API Key

## Быстрый старт

1. Создай `.env` на основе `.env.example`.
2. Заполни обязательные переменные:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENROUTER_API_KEY`
   - `OPENROUTER_BASE_URL` (обычно `https://openrouter.ai/api/v1`)
   - `LLM_MODEL`
   - `SYSTEM_PROMPT`
   - `LOG_LEVEL`

## Локальный запуск (без Docker)

- `make install` — установить зависимости через `uv`.
- `make run` — запустить бота.

## Запуск в Docker

- `make docker-build` — собрать Docker-образ.
- `make docker-up` — поднять контейнер через compose.
- `make docker-down` — остановить контейнер.

## Полезные команды

- `make lint` — проверить стиль кода.
- `make test` — запустить тесты.

## Документация

- Концепция: `docs/idea.md`
- Техническое видение: `docs/vision.md`
