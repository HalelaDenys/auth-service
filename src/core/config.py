from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, AmqpDsn
from typing import ClassVar
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class MiddlewareConfig(BaseModel):
    cors_allowed_origins: list[str]


class DBConfig(BaseModel):
    naming_convention: ClassVar[dict] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    echo: bool = False

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


class AuthConfig(BaseModel):
    secret_key: str
    access_expire_day: int
    refresh_expire_day: int
    algorithm: str = "HS256"
    reset_token_expire_minute: int


class EmailConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 1025
    from_email: str = "admin@example.com"
    username: str | None = None
    password: str | None = None


class BrokerConfig(BaseModel):
    rabbit_url: AmqpDsn = "amqp://guest:guest@localhost:5672/"
    enable_broker: bool = True
    with_real: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="APP_CONFIG__",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    db: DBConfig
    midd: MiddlewareConfig
    jwt: AuthConfig
    mode: str
    mail: EmailConfig = EmailConfig()
    br: BrokerConfig = BrokerConfig()


settings = Settings()
