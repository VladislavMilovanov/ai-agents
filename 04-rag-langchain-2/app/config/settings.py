from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SBER_SYSTEM_PROMPT = (
    "Ты — ассистент по продуктам и услугам Сбербанка (потребительские кредиты, вклады, "
    "справочная информация для клиентов). Отвечай на русском языке вежливо и по делу, "
    "как консультант банка. Опирайся только на фрагменты документов из контекста запроса; "
    "не выдумывай тарифы, ставки, сроки и условия, которых нет в контексте. "
    "Если в контексте нет ответа — честно скажи, что по имеющимся материалам ответить нельзя."
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str = Field(min_length=1)
    openrouter_api_key: str = Field(min_length=1)
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = Field(min_length=1)
    embedding_model: str = Field(min_length=1)
    system_prompt: str = Field(default=DEFAULT_SBER_SYSTEM_PROMPT, min_length=1)
    retriever_k: int = Field(gt=0)
    history_max_pairs: int = Field(default=10, gt=0)
    llm_timeout_sec: int = Field(default=60, gt=0)
    log_level: str = "INFO"
    data_dir: str = "data"
    chunk_size: int = Field(default=1000, ge=100)
    chunk_overlap: int = Field(default=200, ge=0)
    openrouter_http_referer: str | None = None
    openrouter_x_title: str | None = None

    @field_validator(
        "telegram_bot_token",
        "openrouter_api_key",
        "llm_model",
        "embedding_model",
        "system_prompt",
        "data_dir",
        "openrouter_base_url",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("openrouter_base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        if not value.lower().startswith(("http://", "https://")):
            msg = "OPENROUTER_BASE_URL must be an absolute HTTP(S) URL"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_chunk_params(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            msg = "CHUNK_OVERLAP must be less than CHUNK_SIZE"
            raise ValueError(msg)
        return self

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)
