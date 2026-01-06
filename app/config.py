from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_mode: str = "sqlite"  # sqlite | memory
    database_url_sqlite: str = "sqlite:///data/boardgames.db"
    database_url_memory: str = "sqlite://"
    database_echo: bool = False

    @property
    def database_url(self) -> str:
        if self.db_mode == "memory":
            return self.database_url_memory
        return self.database_url_sqlite

    model_config = SettingsConfigDict(env_prefix="BOARDGAME_", env_file=".env", extra="ignore")


settings = Settings()
