from fastapi import FastAPI
from core.handlers import register_exception_handler
from api.user import user_router
app = FastAPI()

register_exception_handler(app)

app.include_router(user_router,prefix="/user")