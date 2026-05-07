from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # DB
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "nkg"

    # JWT
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_min: int = 1440
    jwt_algorithm: str = "HS256"

    # LLM
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_model: str = "abab6.5s-chat"
    llm_mock: bool = True

    # RAG (reserved)
    rag_enabled: bool = False
    embedding_model: str = "minimax-embedding-001"
    embedding_dim: int = 1024

    # SQL Console
    sql_console_enabled: bool = True

    @property
    def db_url(self) -> str:
        return (f"mysql+pymysql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4")


settings = Settings()
