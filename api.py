from pydantic import BaseModel
from typing import Union, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis import Redis

from settings import settings
from tg_auth import Auth

import jwt

app = FastAPI(host=settings.server_ip.get_secret_value(), port=8000)
redis = Redis(host=settings.redis_ip, port=6379, db=0, decode_responses=True)
auth = Auth(library_name=settings.library_name, session_path=settings.tg_session_path)

SECRET_KEY = settings.jwt_token.get_secret_value()
ALGORITHM = "HS256"


class UserData(BaseModel):
    user_id: int
    api_id: int
    api_hash: str
    phone_number: str
    cloud_password: Optional[Union[str, bool]] = None

class TelegramCode(BaseModel):
    user_id: int
    verify_code: int


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = self.decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid
    
    def decode_jwt(self, token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except:
            return {}



# client-side
def _acces_token_encode() -> str:
    encoded = jwt.encode({'sub': None}, SECRET_KEY, algorithm=ALGORITHM)

def _access_token_decode(token: str) -> dict:
    SECRET_KEY = 'JWT_token_key'  # replace with your secret key(better to get this from environment variables)
    jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def _request_query():
    headers = {
        "Authorization": f'Bearer {"token"}',
        "Content-Type": "application/json"
    }
    httpx.post('url', json='data', headers=headers)
#


@app.post('/api', dependencies=[Depends(JWTBearer())], tags=["posts"])
async def receive_api(data: UserData):
    
    # Access the received data
    user_id = data.user_id
    api_id = data.api_id
    api_hash = data.api_hash
    phone_number = data.phone_number
    cloud_password = str(data.cloud_password) if data.cloud_password is not None else None
    print(user_id, api_id, api_hash, phone_number, cloud_password, type(cloud_password))
    # erros
    if len(api_hash) != 32 or (len(phone_number) <= 8 and len(phone_number)) > 13:
        raise HTTPException(status_code=400, detail="Invalid API data")
    
    phone_number = '+' + phone_number.replace('+', '')
    
    # Write the data to redis 
    if cloud_password:
        print(1)
        redis.set(f'userbot_apis:{user_id}', f'{api_id}:{api_hash}:{phone_number}:{cloud_password}')
    else:
        print(2)
        redis.set(f'userbot_apis:{user_id}', f'{api_id}:{api_hash}:{phone_number}')
    redis.expire(f'userbot_apis:{user_id}', 240)
    
    api_data = redis.get(f'userbot_apis:{user_id}')
    
    parts = api_data.split(':')
    api_id = int(parts[0])
    api_hash = parts[1]
    phone_number = parts[2]
    cloud_password = (parts[-1] if len(parts) > 3 else None)
    
    client = auth.client_obj_fabric(user_id, api_id, api_hash, phone_number, cloud_password)
    
    await auth.send_code(client)
    
    return {"message": "Data received successfully"}

@app.post('/api/verify_code', dependencies=[Depends(JWTBearer())], tags=["posts"])
async def receive_api_code(code: TelegramCode):
    
    # errors
    if len(str(code.verify_code)) != 5:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Write the data to redis
    redis.set(f'userbot_apis:{code.user_id}:code', code.verify_code)
    redis.expire(f'userbot_apis:{code.user_id}:code', 60)
    
    api_data = redis.get(f'userbot_apis:{code.user_id}')
    print(api_data)
    # errors
    if not api_data:
        raise HTTPException(status_code=400, detail="API expired")
    
    parts = api_data.split(':')
    api_id = int(parts[0])
    api_hash = parts[1]
    phone_number = parts[2]
    cloud_password = (parts[-1] if len(parts) > 3 else None)
    
    client = auth.client_obj_fabric(code.user_id, api_id, api_hash, phone_number, cloud_password)
    
    client_logon = await auth.sign_in(client, code.verify_code)
    
    print(client_logon)
    
    return {"message": "Code received successfully"}

