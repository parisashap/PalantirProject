from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    FOUNDRY_HOSTNAME: str = "your-instance.palantirfoundry.com"
    FOUNDRY_TOKEN: str = "your_token_here"
    FOUNDRY_CLIENT_ID: str = ""
    FOUNDRY_CLIENT_SECRET: str = ""
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
