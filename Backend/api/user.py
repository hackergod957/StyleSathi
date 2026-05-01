from fastapi import APIRouter
from services.users import updateUser,getUser,createUser
from schemas.UpdateBody import updateReq    
from core.AppException import AppException
from services.users import getUser
from fastapi.security import HTTPBearer
from fastapi import Depends
from dotenv import load_dotenv
from supabase import create_client , Client
import os 

load_dotenv()

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL") 
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY") 


user_router = APIRouter()
security = HTTPBearer()
supabase : Client = create_client(SUPABASE_PROJECT_URL,SUPABASE_API_KEY)
def get_supabase(token: str):
    client = create_client(SUPABASE_PROJECT_URL, SUPABASE_API_KEY)
    client.postgrest.auth(token)  
    return client




def checkAuth(credentials=Depends(security)):
    token = credentials.credentials

    user = supabase.auth.get_user(token)
    if not user or not user.user:
        raise AppException("Invalid token",401)

    return {
        "sub": user.user.id,
        "email": user.user.email,
        "token": token
    }
    
    

@user_router.get("/me")
def get_me(info=Depends(checkAuth)):
    client = get_supabase(info["token"])
    try:
        user = getUser(client,info["sub"])
    except AppException:
        user = createUser(client,info)
    return user


@user_router.patch("/me/update")
def update_me(updateReq: updateReq, info=Depends(checkAuth)):
    client = get_supabase(info["token"])
    updateBody = updateReq.model_dump(exclude_unset=True)
    return updateUser(client,info["sub"], updateBody)


@user_router.get("/me/tries")
def getTries(info=Depends(checkAuth)):
    client = get_supabase(info["token"])
    user = getUser(client,info["sub"])
    if user["subscription_status"] != "active":
        return {
            "used": user["free_tries_used"],
            "limit": user["free_tries_limit"],
            "remaining": user["free_tries_limit"] - user["free_tries_used"]
        }
    else:
        return {
            "daily_limit" : user["daily_limit"] - user["user_usage"]
        }
