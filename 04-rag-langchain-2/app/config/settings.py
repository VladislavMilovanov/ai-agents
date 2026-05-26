from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    system_prompt: str = Field(min_length=1)
    history_max_pairs: int = Field(default=10, gt=0)
    llm_timeout_sec: int = Field(default=60, gt=0)
    log_level: str = "INFO"
    openrouter_http_referer: str | None = None
    openrouter_x_title: str | None = None

    @field_validator(
        "telegram_bot_token",
        "openrouter_api_key",
        "llm_model",
        "system_prompt",
        mode="before",
    )
    @classmethod
    def strip_required_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value
