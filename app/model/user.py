from pydantic import BaseModel


class UserData(BaseModel):
    user_id: int
    api_id: int
    api_hash: str
    phone_number: str

class TelegramCode(BaseModel):
    user_id: int
    verify_code: int