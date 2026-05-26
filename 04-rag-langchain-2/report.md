# Отчёт: Telegram RAG-бот (продукты Сбера)

## Название и описание

**Telegram RAG-бот (продукты Сбера)** — Telegram-бот на **aiogram 3** и **LangChain**, который ведёт диалог с памятью и отвечает на вопросы по локальному корпусу документов Сбербанка (потребительский кредит, вклады, справка FAQ) через **RAG**: query transformation → семантический поиск в **InMemoryVectorStore** → ответ LLM с опорой на найденные чанки. Провайдер моделей — **OpenRouter**.

Подробнее: [README.md](README.md), архитектура — [docs/vision.md](docs/vision.md).

## Вариант

**AIDD** — разработка по итерациям из [docs/tasklist.md](docs/tasklist.md) с техвидением [docs/vision.md](docs/vision.md), правилами Cursor (workflow/conventions) и composition root в `app/` (эволюция Спринта 1, без каркаса `src/` из учебного шаблона `04-rag-langchain`).

---

## Реализованные возможности

- [x] Long polling, только личные чаты (`private`)
- [x] Команда `/start` — приветствие (история не сбрасывается)
- [x] Текстовый диалог с RAG и учётом истории (`HumanMessage` / `AIMessage`, лимит пар — `HISTORY_MAX_PAIRS`)
- [x] **Query transformation** перед поиском (отдельный вызов LLM с историей)
- [x] Семантический поиск топ-**K** (`RETRIEVER_K`) в `InMemoryVectorStore`
- [x] Загрузка корпуса: 2 PDF + JSON FAQ из `data/`
- [x] Индексация: `RecursiveCharacterTextSplitter` для PDF; JSON — **без чанкинга** (одна запись = один документ)
- [x] Полная переиндексация при **старте** и по `/index`
- [x] `/index_status` — число чанков в индексе
- [x] Системный промпт — ассистент по продуктам Сбера, ответ только по контексту
- [x] Конфигурация через `Settings` / `.env` (без хардкода секретов)
- [x] Обработка граничных случаев: не текст, пустой текст, ошибки LLM, пустой индекс
- [x] `make lint`, `make test`, Docker / docker compose
- [x] Документация: README, idea, vision, tasklist

---

## Стек и модели

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.12 |
| Зависимости | uv (`pyproject.toml`, `uv.lock`) |
| Telegram | aiogram 3.x, polling |
| RAG / LLM | LangChain (`langchain`, `langchain-openai`, `langchain-community`, `langchain-text-splitters`) |
| PDF | pypdf (`PyPDFLoader`) |
| Векторное хранилище | `InMemoryVectorStore` |
| Конфиг | pydantic-settings, `.env` |
| Качество | ruff, pytest |

### Модели (OpenRouter)

| Назначение | Переменная | Значение в проекте |
|------------|------------|-------------------|
| Чат (query transform + ответ) | `LLM_MODEL` | `openrouter/owl-alpha` (в `.env`; в `.env.example` — `openrouter/free`) |
| Эмбеддинги | `EMBEDDING_MODEL` | `openai/text-embedding-3-small` |
| Топ-K retrieval | `RETRIEVER_K` | `4` |

Параметры чанкинга (текущие в `.env`): `CHUNK_SIZE=1500`, `CHUNK_OVERLAP=150`.

---

## Эксперименты с чанкингом

Сплиттер: `RecursiveCharacterTextSplitter` в `app/rag/index_service.py`. Параметры задаются через `CHUNK_SIZE` / `CHUNK_OVERLAP` в `.env`. PDF режутся сплиттером; **212 записей JSON** индексируются целиком (по полю `full_text`).

| Вариант | `CHUNK_SIZE` / `CHUNK_OVERLAP` | PDF-чанков | JSON-документов | Всего чанков | Наблюдения |
|---------|-------------------------------|------------|-----------------|--------------|------------|
| Базовый (дефолт vision / `.env.example`) | 1000 / 200 | 211 | 212 | **423** | Больше мелких фрагментов PDF; FAQ уже по одной записи |
| Увеличенные чанки (текущий `.env`) | 1500 / 150 | 132 | 212 | **344** | Меньше чанков PDF (~−37%); крупнее контекст в одном чанке — удобнее для связных абзацев условий кредита/вкладов |
| Сепараторы под PDF | — | — | — | не внедрялось | В `Settings` нет поля для `separators`; для эксперимента нужна правка кода в `IndexService` (например `["\n\n", "\n", ". ", " "]`) |

**Выводы:**

1. Увеличение `chunk_size` до 1500 с перекрытием 150 **снижает число PDF-чанков** без изменения FAQ (212).
2. Для вопросов по **картам и справке** важнее отдельная логика JSON (целая запись FAQ), а не размер PDF-чанка.
3. Для продакшн-настроек оставлен вариант **1500/150** — баланс между полнотой контекста в чанке и стоимостью/временем индексации.
4. Эксперимент с **кастомными separators** оставлен на будущее; дефолтные сепараторы LangChain использовались во всех прогонах.

Проверка: после смены параметров — перезапуск бота (переиндексация при старте) или `/index`, затем `/index_status` и одни и те же тестовые вопросы в Telegram.

---

## JSON: загрузка корпуса

### Как в учебном примере (JSONLoader)

Ориентир из задания:

```python
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path=str(json_path),
    jq_schema=".[] | .full_text",
    text_content=False,
)
documents = loader.load()
```

Каждый элемент массива → документ с текстом из `full_text`.

### Как реализовано в проекте

Используется **`CorpusLoader`** (`app/rag/corpus_loader.py`): **`JSONLoader` не подключён** — эквивалентная логика на `json.loads` и `Document`:

- файл `data/sberbank_help_documents.json` — массив объектов;
- для каждой записи с непустым `full_text` создаётся `Document(page_content=full_text, metadata={"source": ..., "url": ...})`;
- PDF загружаются через **`PyPDFLoader`**.

В **`IndexService.rebuild()`** документы делятся на PDF и JSON по `metadata["source"]`:

- PDF → `RecursiveCharacterTextSplitter.split_documents`;
- JSON → в индекс **без разбиения** (212 документов = 212 чанков).

**Зачем так:** один FAQ-ответ не разрывается на части; вопросы вроде «Как заказать карту?» / «Как активировать карту?» попадают в retrieval целиком по записи справки.

**Сравнение с JSONLoader:** семантика та же (одна запись — один документ); ручной парсер проще отлаживать и не требует `jq` в окружении.

---

## Сравнение эмбеддингов

Все вызовы — `OpenAIEmbeddings` через OpenRouter (`OPENROUTER_BASE_URL`, `EMBEDDING_MODEL`).

| Модель | Результат | Вывод |
|--------|---------|--------|
| `openai/text-embedding-3-small` | Индексация успешна, RAG отвечает | **Рабочая модель по умолчанию** — стабильный API эмбеддингов, разумная цена/качество для русскоязычного корпуса |
| `nvidia/llama-nemotron-embed-vl-1b-v2:free` | Пустой ответ API при `embed_documents`, индекс **0 чанков**, `RAG ready=False` | **Не подходит** для этого пайплайна (мультимодальная/free-модель не отдаёт векторы в формате, ожидаемом LangChain OpenAI embeddings) |

**Итог:** для бота зафиксирована **`openai/text-embedding-3-small`**. Бесплатные «embed»-модели на OpenRouter нужно проверять отдельным прогоном `IndexService.rebuild()` и `/index_status` перед использованием в диалоге.

LLM для чата (`openrouter/owl-alpha`) с эмбеддингами не смешивается — отдельная переменная `LLM_MODEL`.

---

## Ссылки

- [README.md](README.md) — запуск и env
- [docs/vision.md](docs/vision.md) — архитектура
- [docs/tasklist.md](docs/tasklist.md) — итерации разработки
- [docs/idea.md](docs/idea.md) — идея продукта
