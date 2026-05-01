from fastapi import APIRouter,Depends
from api.user import checkAuth
from services.subscriber import getPlan,getPlans
from core.AppException import AppException
from schemas.planBody import planReq
from schemas.pidxBody import pidxReq
from services.subscriber import InitiateSubscribe,verifyPayment
from fastapi.security import HTTPBearer

subscription_router = APIRouter()
security = HTTPBearer()


@subscription_router.get("/plans")
def plans():
    return getPlans()


@subscription_router.post("/create")
def create_subscribe(planReq : planReq,credentials=Depends(security)):

    planId = planReq.planId
    info = checkAuth(credentials)
    plan = getPlan(planId)

    if plan is None:
        raise AppException("Plan not found", 404)
    
    data = InitiateSubscribe(plan,info["sub"])

    return data

@subscription_router.post("/verify")
def verify_subscribe(payload : pidxReq ,credentials=Depends(security)):

    info = checkAuth(credentials)
    pidx = payload.pidx
    
    data = verifyPayment(pidx)

    return data