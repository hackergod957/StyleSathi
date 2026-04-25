from pydantic import BaseModel
from typing import Optional


class  updateReq(BaseModel) : 
    email : Optional[str] 
    vibes : Optional[list[str]]
    language_preference : Optional[str]
    free_tries_used : Optional[int]
    subscription_status :Optional[str]
    profile_photo_url : Optional[str]
    onboarding_completed : Optional[bool]