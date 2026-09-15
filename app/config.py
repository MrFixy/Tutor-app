from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tutor:tutor@localhost:5432/tutor_db"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120
    app_env: str = "dev"

    # Phase 3 / Week 7-8: self-hosted Judge0 (docker-compose.judge0.yml)
    judge0_url: str = "http://localhost:2358"
    judge0_timeout: int = 30
    # Judge0 CE language id for Python 3. See:
    # GET {judge0_url}/languages to confirm on your instance.
    judge0_python_language_id: int = 71

    # Phase 6 / Week 14: latency tuning. A single local Ollama instance
    # (one GPU, one loaded model) doesn't parallelize across requests --
    # letting several pilot learners hit /chat at once just makes every
    # one of their generations slower via VRAM/context thrashing. Cap
    # concurrent local generations; raise only on hardware that can
    # actually parallelize (or when hosted fallback is absorbing overflow).
    ollama_max_concurrency: int = 1

    # Phase 6 / Week 14: optional hosted-API fallback for when the local
    # Ollama instance is down, mid-model-swap, or out of VRAM during a
    # pilot session. Off by default -- see HOSTED_FALLBACK_DECISION.md for
    # the tradeoffs before turning this on for a wider rollout.
    hosted_fallback_enabled: bool = False
    hosted_provider: str = "anthropic"  # "anthropic" | "openai_compatible"
    hosted_api_key: str = ""
    hosted_api_base: str = "https://api.anthropic.com"
    hosted_model: str = "claude-3-5-haiku-20241022"
    hosted_timeout: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
