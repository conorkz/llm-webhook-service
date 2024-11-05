from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "LLM Webhook Service"
    OPENROUTER_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"
    RABBITMQ_URL: str = "amqp://rabbitmq:5672"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600 

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 