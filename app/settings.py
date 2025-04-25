from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    static_dir: str = "../static"
    template_path: str = "static/template.pdf"
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
