import os
import time
import requests
from jose import jwt
from dotenv import load_dotenv
from supabase import create_client , Client
from core import AppException

load_dotenv()

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL") 
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY") 
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/keys"
jwks_cache = {"keys": None, "time": 0}
supabase : Client = create_client(SUPABASE_PROJECT_URL,SUPABASE_API_KEY)

def get_jwks():
    now = time.time()
    if jwks_cache["keys"] is None or now - jwks_cache["time"] > 3600:
        resp = requests.get(JWKS_URL,headers={"apikey" : SUPABASE_API_KEY}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if "keys" not in data or not data["keys"]:
            raise AppException("Invalid JWKS format",422)
        jwks_cache["keys"] = data["keys"]
        jwks_cache["time"] = now
    return jwks_cache["keys"]

def get_key_by_kid(kid):
    return next((k for k in get_jwks() if k["kid"] == kid), None)

def verify_jwt(token: str):
    header = jwt.get_unverified_header(token)
    kid = header["kid"]
    key = get_key_by_kid(kid)
    if not key:
    
        jwks_cache["keys"] = None
        key = get_key_by_kid(kid)
    if not key:
        raise AppException("No matching JWK found",401)
    public_key = {
        "kty": key["kty"],
        "kid": key["kid"],
        "n": key["n"],

        "e": key["e"],
    }
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="authenticated",        
        issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
    )
   


    return payload


