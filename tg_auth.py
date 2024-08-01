from pyrogram import Client
from pyrogram.types import SentCode
from telethon import TelegramClient
from telethon.tl.types.auth import SentCode as Tl_SentCode

from dataclasses import dataclass, field
from typing import Literal, Optional, Union

@dataclass
class Auth:
    library_name: Literal['pyrogram', 'telethon']
    session_path: str
    # Not required fields
    phone_number: str = field(default=None)
    cloud_password: str = field(default=None)
    requested_phone_code: str = field(default=None)
    
    def client_obj_fabric(
        self,
        user_id: int,
        api_id: int,
        api_hash: str,
        phone_number: str,
        cloud_password: str = None,
        session_name: str = None
    ) -> Union[Client, TelegramClient]:
        self.phone_number = phone_number
        self.cloud_password = cloud_password
        session_path = (self.session_path if self.session_path[-1] == '/' else self.session_path + '/')
        if self.library_name == 'pyrogram':
            return Client(
                session_path + (session_name if session_name else str(user_id)),
                api_id, api_hash,
                phone_number = phone_number,
                password = cloud_password,
            )
        else:
            return TelegramClient(
                session_path + (session_name if session_name else str(user_id)),
                api_id, api_hash,
                phone_number = phone_number,
                password = cloud_password,
            )
    
    async def send_code(self, client: [Client, TelegramClient]) -> Union[SentCode, Tl_SentCode]:
        if self.library_name == 'pyrogram':
            await client.connect()
            self.requested_phone_code = await client.send_code(self.phone_number)
            await client.disconnect()
        else:
            self.requested_phone_code = await client.send_code_request(self.phone_number)
    
    async def sign_in(self, client:  [Client, TelegramClient], code: str):
        if self.library_name == 'pyrogram':
            print(client, self.phone_number, self.requested_phone_code, code)
            print(self.phone_number, self.requested_phone_code.phone_code_hash, str(code))
            await client.connect() # PROBLEM IS HERE
            return await client.sign_in(self.phone_number, self.requested_phone_code.phone_code_hash, str(code))
            await client.disconnect()
        else:
            # await client.start()
            return await client.sign_in(self.phone_number, code, phone_code_hash=self.requested_phone_code.phone_code_hash, password=self.cloud_password)
    

