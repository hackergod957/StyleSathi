from fastapi.responses import JSONResponse
from core.AppException import AppException


def register_exception_handler(app):   
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc:AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail" : exc.message}
        )