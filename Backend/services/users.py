import os
from dotenv import load_dotenv
from supabase import create_client , Client
from core import AppException
load_dotenv()

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL") 
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY") 
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/keys"
supabase : Client = create_client(SUPABASE_PROJECT_URL,SUPABASE_API_KEY)

def createUser(user):
    try : 
        newUser = supabase.table("public.users").insert({"id":user["sub"], "email":user.get("email")}).execute()

    except:
         raise AppException("Error while creation",500)
    
    return newUser.data[0]


def getUser(id): 
        user  = supabase.table("public.users").select("*").eq("id",id).execute()

        if not user.data :
            raise AppException(f"User doesn't exist",404)

        return user.data[0]



def updateUser(id,userData):
   
    try : 
        user  = supabase.table("public.users").update(userData).eq("id",id).execute()

    except:
         raise AppException(f"Error During user update",500)

    if not user.data :
        raise AppException(f"User doesn't exist",404)
    
    return user.data[0]