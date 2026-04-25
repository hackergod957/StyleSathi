from fastapi import APIRouter, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from Backend.services.auth import verify_jwt
from Backend.services.users import updateUser,getUser,createUser
from Backend.schemas.UpdateBody import updateReq    
from core import AppException



user_router = APIRouter()

   
@user_router.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization:
        raise AppException(401, "Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise AppException(401, "Invalid Authorization format")

    token = authorization.split(" ")[1]
    try:
        info = verify_jwt(token)
    except Exception as e:
        raise AppException(401, f"Invalid token: {str(e)}")
    
    try:
        user = getUser(info["sub"])

    except AppException:
        user = createUser(info)
    return user


@user_router.patch("/me/update")
def update_me(updateReq : updateReq , authorization: str = Header(None)):
    if not authorization:
        raise AppException(401, "Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise AppException(401, "Invalid Authorization format")

    token = authorization.split(" ")[1]
    
    info = verify_jwt(token)
  
    
    updateBody = updateReq.model_dump(exclude_unset=True)
    user = updateUser(info["sub"],updateBody)
    
    
    return user