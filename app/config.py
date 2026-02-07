from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_mode: str = "sqlite"  # sqlite | memory
    database_url_sqlite: str = "sqlite:///data/boardgames.db"
    database_url_memory: str = "sqlite://"
    database_echo: bool = False
    redis_url: str = "redis://localhost:6379/0"
     # ===== Security / JWT =====
    jwt_secret_key: str = "CHANGE_ME"          
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 30

    admin_username: str = "admin"
    admin_password_hash: str = ""              


    @property
    def database_url(self) -> str:
        if self.db_mode == "memory":
            return self.database_url_memory
        return self.database_url_sqlite

    model_config = SettingsConfigDict(env_prefix="BOARDGAME_", env_file=".env", extra="ignore")


settings = Settings()
