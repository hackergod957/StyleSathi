from fastapi import APIRouter, Header
from services.auth import verify_jwt
from services.users import updateUser,getUser,createUser
from schemas.UpdateBody import updateReq    
from core import AppException
from services.users import getUser


user_router = APIRouter()


   
@user_router.get("/me")
def get_me(authorization: str = Header(None)):
    
    info = checkAuth(authorization)
    
    try:
        user = getUser(info["sub"])

    except AppException:
        user = createUser(info)
    return user


@user_router.patch("/me/update")
def update_me(updateReq : updateReq , authorization: str = Header(None)):
   
    info = checkAuth(authorization)
    
    updateBody = updateReq.model_dump(exclude_unset=True)
    user = updateUser(info["sub"],updateBody)
    
    
    return user


@user_router.get("/me/tries")
def getTries(authorization: str = Header(None)):
    
    info = checkAuth(authorization)
    
    user = getUser(info["sub"])

    return {
        "used": user["free_tries_used"],
        "limit": user["free_tries_limit"],
        "remaining": user["free_tries_limit"] - user["free_tries_used"]
    }


def checkAuth( authorization: str = Header(None)):
    if not authorization:
        raise AppException("Missing Authorization header",401)
    if not authorization.startswith("Bearer "):
        raise AppException("Invalid Authorization format",401)

    token = authorization.split(" ")[1]
    try:
        info = verify_jwt(token)
    except Exception as e:
        raise AppException(f"Invalid token: {str(e)}",401)
    
    return info