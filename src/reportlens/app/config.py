from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llama_parse_api_key: str
    out_dir: str
    cache_dir: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()