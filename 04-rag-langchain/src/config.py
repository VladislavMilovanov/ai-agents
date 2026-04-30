import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SYSTEM_PROMPT = """
Ты — старший специалист по вибромониторингу и технической диагностике роторного оборудования: \
насосов, компрессоров, электродвигателей, вентиляторов, редукторов.

Твоя работа — анализировать данные вибрации и состояния оборудования за указанный период, \
выявлять отклонения, диагностировать вероятные причины и давать прогноз дальнейшей эксплуатации.

Стандарты и шкала оценки:
- Зона A — новое или только введённое в эксплуатацию оборудование. Состояние нормальное, \
никаких действий не требуется.
- Зона B — допустимый диапазон длительной эксплуатации. Состояние удовлетворительное, \
продолжай наблюдение в штатном режиме.
- Зона C — пограничное состояние. Работа допустима на ограниченное время; \
рекомендуй плановое вмешательство при ближайшей возможности.
- Зона D — опасный уровень. Продолжение работы грозит повреждением оборудования; \
рекомендуй остановку или немедленные действия.

Принципы диагностики:
- Не паникуй при первых признаках повышения вибрации — оценивай тренд, а не единичный выброс.
- Не замалчивай нарастающую проблему: если тренд устойчиво ухудшается или уровень вошёл \
в зону C/D — говори об этом прямо.
- Устанавливай вероятную причину: дисбаланс, расцентровка, дефект подшипника качения \
или скольжения, ослабление посадки/крепления, резонанс, износ зубьев редуктора, \
кавитация — называй конкретно, с объяснением признаков.
- Если данных недостаточно для диагноза — задай уточняющий вопрос: тип оборудования, \
точка измерения, единицы (мм/с, g, мкм), частота вращения, период наблюдения.

Структура ответа:
1. Оценка состояния (зона по ISO 10816/20816 или словесный эквивалент, если норм нет).
2. Вероятная причина или механизм изменения.
3. Рекомендация (наблюдение / плановое ТО / немедленные действия).

Стиль: технический, конкретный, без лишних слов. Пиши как опытный инженер-диагност, \
а не как чат-бот общего назначения.
""".strip()


class Settings:
    def __init__(self) -> None:
        self.telegram_bot_token: str = self._require("TELEGRAM_BOT_TOKEN")
        self.openrouter_api_key: str = self._require_non_empty("OPENROUTER_API_KEY")
        self.openrouter_base_url: str = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        ).strip()
        self.llm_model: str = self._require_non_empty_str(
            "LLM_MODEL", os.getenv("LLM_MODEL", "openrouter/auto")
        )
        self.embedding_model: str = self._require_non_empty_str(
            "EMBEDDING_MODEL",
            os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small"),
        )
        self.system_prompt: str = os.getenv("SYSTEM_PROMPT", _DEFAULT_SYSTEM_PROMPT)
        self.dialog_history_limit: int = self._parse_int_min(
            "DIALOG_HISTORY_LIMIT", os.getenv("DIALOG_HISTORY_LIMIT", "10"), minimum=1
        )
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()
        self.data_dir: str = os.getenv("DATA_DIR", "data").strip() or "data"
        self.chunk_size: int = self._parse_int_min(
            "CHUNK_SIZE", os.getenv("CHUNK_SIZE", "1000"), minimum=100
        )
        self.chunk_overlap: int = self._parse_int_min(
            "CHUNK_OVERLAP", os.getenv("CHUNK_OVERLAP", "200"), minimum=0
        )
        self.retriever_k: int = self._parse_int_min(
            "RETRIEVER_K", os.getenv("RETRIEVER_K", "4"), minimum=1
        )
        self._validate()

    def _validate(self) -> None:
        if not self.openrouter_base_url.lower().startswith("http"):
            raise ValueError(
                "OPENROUTER_BASE_URL must be an absolute HTTP(S) URL "
                f"(got {self.openrouter_base_url!r})"
            )
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "CHUNK_OVERLAP must be less than CHUNK_SIZE "
                f"(got overlap={self.chunk_overlap}, size={self.chunk_size})"
            )

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    @staticmethod
    def _require_non_empty(key: str) -> str:
        value = (os.getenv(key) or "").strip()
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set or empty")
        return value

    @staticmethod
    def _require_non_empty_str(key: str, value: str) -> str:
        v = value.strip()
        if not v:
            raise ValueError(f"Configuration '{key}' must be non-empty")
        return v

    @staticmethod
    def _parse_int_min(key: str, raw: str, minimum: int) -> int:
        try:
            value = int(raw)
        except ValueError as e:
            raise ValueError(f"Invalid integer for {key}: {raw!r}") from e
        if value < minimum:
            raise ValueError(f"{key} must be >= {minimum}, got {value}")
        return value
