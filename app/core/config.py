from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

from fastapi import FastAPI
from redis import Redis

from app.auth.tg_auth import TGAuth

import os

ENV: str = ''


class Configs(BaseSettings):
    # base
    project_name: str = 'epidemic-api'
    library_name: str = 'pyrogram'
    
    project_root: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # date
    datetime_format: str = "%Y-%m-%dT%H:%M:%S"
    date_format: str = "%Y-%m-%d"
    
    # auth
    secret_key: str
    algorithm: str = 'HS256'
    
    # CORS
    backend_cors_origins: List[str] = ["*"]
    
    # redis
    redis_host: str
    tg_session_path: str
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


configs = Configs()

redis = Redis(host=configs.redis_host, port=6379, db=0, decode_responses=True)
tgauth = TGAuth(library_name=configs.library_name, session_path=configs.tg_session_path, redis=redis)

