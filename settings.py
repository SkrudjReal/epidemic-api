from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    server_ip: SecretStr
    redis_ip: str
    tg_session_path: str
    library_name: str
    jwt_token: SecretStr
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()
