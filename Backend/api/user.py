from fastapi import APIRouter, Header
from services.auth import verify_jwt
from services.users import updateUser,getUser,createUser
from schemas.UpdateBody import updateReq    
from core import AppException



user_router = APIRouter()

   
@user_router.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization:
        raise AppException("Missing Authorization header",401)
    if not authorization.startswith("Bearer "):
        raise AppException("Invalid Authorization format",401)

    token = authorization.split(" ")[1]
    try:
        info = verify_jwt(token)
    except Exception as e:
        raise AppException(f"Invalid token: {str(e)}",401)
    
    try:
        user = getUser(info["sub"])

    except AppException:
        user = createUser(info)
    return user


@user_router.patch("/me/update")
def update_me(updateReq : updateReq , authorization: str = Header(None)):
    if not authorization:
        raise AppException("Missing Authorization header",401)
    if not authorization.startswith("Bearer "):
        raise AppException("Invalid Authorization format",401)

    token = authorization.split(" ")[1]
    
    info = verify_jwt(token)
  
    
    updateBody = updateReq.model_dump(exclude_unset=True)
    user = updateUser(info["sub"],updateBody)
    
    
    return user