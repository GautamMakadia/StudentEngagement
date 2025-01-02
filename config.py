from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Env(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    FIREBASE_CONF: str
    FIREBASE_STORAGE_BUCKET: str
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

@lru_cache
def get_env():
    return Env()

env: Env = get_env()