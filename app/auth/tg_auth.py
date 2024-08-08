from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, BadRequest
from telethon import TelegramClient

from fastapi import HTTPException

from dataclasses import dataclass
from typing import Literal, Union, Callable
from redis import Redis

import asyncio
import os

@dataclass
class TGAuth:
    library_name: Literal['pyrogram', 'telethon']
    redis: Redis
    session_path: str
    
    def client_obj_fabric(
        self,
        user_id: int,
        api_id: int,
        api_hash: str,
        phone_number: str,
    ) -> Union[Client, TelegramClient]:
        session_path = (self.session_path[:-1] if self.session_path[-1] == '/' else self.session_path)
        if self.library_name == 'pyrogram':
            return Client(
                str(user_id),
                api_id, api_hash,
                phone_number = phone_number,
                in_memory=False,
                workdir=session_path
            )
        else:
            return TelegramClient(
                str(user_id),
                api_id, api_hash,
                phone_number = phone_number,
            )
    
    async def sign_in(self, client:  [Client, TelegramClient], user_api: Callable):
        session_path = (self.session_path[:-1] if self.session_path[-1] == '/' else self.session_path)
        if self.library_name == 'pyrogram':
            await client.connect()
            requested_phone_code = await client.send_code(user_api.phone_number)
            
            for _ in range(120):
                code = self.redis.get(f'userbot_apis:{user_api.user_id}:code')
                if code:
                    self.redis.delete(f'userbot_apis:{user_api.user_id}:code', f'userbot_apis:{user_api.user_id}')
                    break
                await asyncio.sleep(1)
            
            if not code:
                raise HTTPException(status_code=408, detail='Request Timeout. We not received verify code from client')
            try:
                await client.sign_in(user_api.phone_number, requested_phone_code.phone_code_hash, str(code))
            except SessionPasswordNeeded:
                raise HTTPException(status_code=403, detail="User doesn't disable 2-fa.")
            except BadRequest:
                raise HTTPException(status_code=403, detail="Something went wrong while sign-in client.")
            else:
                self.redis.set(f'userbot_apis:{user_api.user_id}:ok', 1)
            finally:
                await client.disconnect()
            return True
        else:
            requested_phone_code = await client.send_code_request(user_api.phone_number)
            result = await client.sign_in(user_api.phone_number, code, phone_code_hash=requested_phone_code.phone_code_hash, password=user_api.cloud_password)
    

