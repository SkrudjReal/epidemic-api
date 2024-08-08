from fastapi import FastAPI

from app.api.routes import routers
from app.core.config import configs
from app.util.class_object import singleton


@singleton
class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=configs.project_name,
            version='1.0',
            port=8000
        )

        # set routes
        @self.app.get("/")
        def root():
            return "service is working"

        self.app.include_router(routers)


app_creator = AppCreator()
app = app_creator.app
#  client-side
# def _acces_token_encode() -> str:
#     encoded = jwt.encode({'sub': None}, SECRET_KEY, algorithm=ALGORITHM)

# def _access_token_decode(token: str) -> dict:
#     SECRET_KEY = 'JWT_token_key'  # replace with your secret key(better to get this from environment variables)
#     jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

# def _request_query():
#     headers = {
#         "Authorization": f'Bearer {"token"}',
#         "Content-Type": "application/json"
#     }
#     httpx.post('url', json='data', headers=headers)
# #