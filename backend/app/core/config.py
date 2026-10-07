from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+psycopg://lms_user:lms_password@localhost:5432/agentic_ai_lms"
    database_url_sync: str = "postgresql+psycopg://lms_user:lms_password@localhost:5432/agentic_ai_lms"
    vector_database_url: str = "postgresql+psycopg://lms_user:lms_password@localhost:5432/agentic_ai_lms"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14

    llm_provider: str = "anthropic"
    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-5"
    embedding_provider: str = "anthropic"
    embedding_api_key: str = ""
    embedding_model: str = "voyage-3"

    # Sandboxed code-execution service (see /code_runner). Empty URL = coding questions cannot be graded.
    code_runner_url: str = ""
    code_runner_token: str = ""

    cors_origins: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    # Per-client-IP request limits (slowapi syntax, e.g. "120/minute"). "auth" applies to login/register only.
    rate_limit_enabled: bool = True
    rate_limit_default: str = "120/minute"
    rate_limit_auth: str = "20/minute"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
