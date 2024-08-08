from fastapi import HTTPException, Depends, APIRouter

from app.model.user import UserData, TelegramCode
from app.auth.auth_bearer import JWTBearer
from app.core.config import redis, tgauth

import asyncio


router = APIRouter(
    tags=["user"],
)


@router.post('/api', dependencies=[Depends(JWTBearer())])
async def receive_api(data: UserData = [Depends(JWTBearer())]):
    # erros
    if len(data.api_hash) != 32 or (len(data.phone_number) <= 8 and len(data.phone_number)) > 13:
        raise HTTPException(status_code=400, detail="Invalid API data")
    
    data.phone_number = '+' + data.phone_number.replace('+', '')
    
    # Write the data to redis 
    redis.set(f'userbot_apis:{data.user_id}', f'{data.api_id}:{data.api_hash}:{data.phone_number}')
    redis.expire(f'userbot_apis:{data.user_id}', 240)
    
    client = tgauth.client_obj_fabric(data.user_id, data.api_id, data.api_hash, data.phone_number)
    
    asyncio.create_task(tgauth.sign_in(client, data))
    
    return {"message": "Data received successfully"}

@router.post('/api/verify_code', dependencies=[Depends(JWTBearer())])
async def receive_api_code(code: TelegramCode):
    
    # errors
    if len(str(code.verify_code)) != 5:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Write the data to redis
    redis.set(f'userbot_apis:{code.user_id}:code', code.verify_code)
    redis.expire(f'userbot_apis:{code.user_id}:code', 120)
    
    return {"message": "Code received successfully"}

@router.get('/api/ok', dependencies=[Depends(JWTBearer())])
async def get_ub_auth_status(user_id: int):
    
    ok = redis.get(f'userbot_apis:{user_id}:ok')
    
    return {'message': ok}

