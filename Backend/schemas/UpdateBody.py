from pydantic import BaseModel
from typing import Optional

class updateReq(BaseModel):
    email: Optional[str] = None
    vibes: Optional[list[str]] = None
    language_preference: Optional[str] = None
    free_tries_used: Optional[int] = None
    subscription_status: Optional[str] = None
    profile_photo_url: Optional[str] = None
    onboarding_completed: Optional[bool] = None