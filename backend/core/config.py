from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    DATABASE_URL: str = "postgresql+asyncpg://sentinel:sentinel_secret@localhost:5432/sentinel"
    DB_POOL_SIZE: int = 20

    REDIS_URL: str = "redis://localhost:6379"

    ANTHROPIC_API_KEY: str = ""

    GITHUB_APP_ID: Optional[str] = None
    GITHUB_APP_PRIVATE_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: str = ""

    GITLAB_URL: str = "https://gitlab.com"
    GITLAB_TOKEN: Optional[str] = None
    GITLAB_WEBHOOK_SECRET: str = ""

    JENKINS_WEBHOOK_SECRET: str = ""
    CIRCLECI_WEBHOOK_SECRET: str = ""

    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_CHANNEL_ID: Optional[str] = None
    PAGERDUTY_ROUTING_KEY: Optional[str] = None
    ESCALATION_EMAIL: Optional[str] = None

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "sentinel@yourcompany.com"

    JWT_SECRET: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    DEFAULT_MAX_ATTEMPTS: int = 3
    SANDBOX_TIMEOUT_SECONDS: int = 300
    SANDBOX_MEMORY_LIMIT: str = "512m"
    SANDBOX_NETWORK: str = "sentinel_sandbox"
    WORKER_CONCURRENCY: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
