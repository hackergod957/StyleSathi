from fastapi import APIRouter,Header
from api.user import checkAuth


subscription_router = APIRouter()


@subscription_router.get("/plans")
def getPlans():
    return {

    "plans": [
        {
           "id": "basic",
                "name": "Basic",
                "order": 1,
                "price": {
                    "amount": 49,
                    "currency": "INR"
                },
                "interval": "month",
                "limits": {
                    "try_on_per_day": 5
                },
                "features": [
                    "Up to 5 try-ons per day",
                    "Standard processing speed",
                    "Email support"
                ]
            },
            {
                "id": "standard",
                "name": "Standard",
                "order": 2,
                "recommended": True,
                "price": {
                    "amount": 99,
                    "currency": "INR"
                },
                "interval": "month",
                "limits": {
                    "try_on_per_day": 10
                },
                "features": [
                    "Up to 10 try-ons per day",
                    "Faster processing",
                    "Priority email support"
                ]
            },
            {
                "id": "pro",
                "name": "Pro",
                "order": 3,
                "price": {
                    "amount": 199,
                    "currency": "INR"
                },
                "interval": "month",
                "limits": {
                    "try_on_per_day": 20
                },
                "features": [
                    "Up to 20 try-ons per day",
                    "Fastest processing",
                    "Priority support + early features"
                ]
            }
        ]
    }


@subscription_router("/create")
def subscribe(authorization : str = Header(None)):
    info = checkAuth(authorization)