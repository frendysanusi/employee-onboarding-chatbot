from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    pinecone_api_key: str = ""
    pinecone_index: str = "umbrella-onboarding"

    cohere_api_key: str = ""

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "onboarding"
    database_user: str = "postgres"
    database_password: str = ""

    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "employee-onboarding-chatbot"

    @property
    def database_url(self) -> str:
        pwd = f":{self.database_password}" if self.database_password else ""
        return (
            f"postgresql://{self.database_user}{pwd}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
