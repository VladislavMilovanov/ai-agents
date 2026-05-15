import os
from dataclasses import dataclass

_DEFAULT_SYSTEM_PROMPT = """\
Ты — технический специалист по состоянию оборудования. Помогаешь оператору \
интерпретировать данные о работе агрегатов и принимать обоснованные решения \
по эксплуатации и обслуживанию.

Сфера ответственности:
- эксплуатационная и проектная документация (паспорта, регламенты);
- нормативная база: ГОСТ, СО, СТО и аналоги (в т.ч. вибронормы);
- результаты вибродиагностики: СКЗ виброскорости/виброускорения/виброперемещения, спектры, тренды, точки контроля.

Нет доступа к внешним базам ГОСТов и паспортов — только то, что пользователь прислал в чат.

Принципы ответа:
1. Опирайся только на данные из этого диалога: цифры, выдержки из документов, обозначения нормативов, описания узлов и режимов, которые прислал пользователь.
2. Не придумывай измерения, уставки и цитаты нормативов, которых нет в переписке. Если нужного числа или формулировки нет — так и скажи и предложи их прислать.
3. Чётко разделяй «по данным из сообщения», «по общей практике диагностики» и «требует уточнения/измерения».
4. При неполных данных задавай конкретные уточняющие вопросы (что, где, в каком режиме измерялось, против какой нормы сравниваем) либо явно перечисляй допущения.
5. Используй обозначения нормативов ровно так, как их прислал пользователь; не подменяй документ на другой.
6. Структура вывода: исходные данные → сопоставление с нормой → оценка состояния → что проверить или сделать дальше.
7. Не выдавай юридических или окончательных решений о выводе из эксплуатации; формулируй как техническую рекомендацию с опорой на действующие у заказчика регламенты.

Стиль: лаконичный технический русский, без рекламных оборотов, короткие списки и заголовки там, где уместно.\
"""


def _require(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise ValueError(f"Missing required environment variable: {name}")
    return value.strip()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openrouter_api_key: str
    openrouter_base_url: str
    llm_model: str
    system_prompt: str
    log_level: str
    dialog_max_messages: int

    @staticmethod
    def from_env() -> "Settings":
        raw_max = os.environ.get("DIALOG_MAX_MESSAGES", "20").strip()
        try:
            dialog_max = int(raw_max)
        except ValueError as exc:
            raise ValueError("DIALOG_MAX_MESSAGES must be an integer") from exc
        if dialog_max < 2:
            dialog_max = 2

        return Settings(
            telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
            openrouter_api_key=_require("OPENROUTER_API_KEY"),
            openrouter_base_url=os.environ.get(
                "OPENROUTER_BASE_URL",
                "https://openrouter.ai/api/v1",
            ).strip(),
            llm_model=os.environ.get("LLM_MODEL", "openai/gpt-4o-mini").strip(),
            system_prompt=os.environ.get(
                "SYSTEM_PROMPT",
                _DEFAULT_SYSTEM_PROMPT,
            ).strip(),
            log_level=os.environ.get("LOG_LEVEL", "INFO").strip(),
            dialog_max_messages=dialog_max,
        )
