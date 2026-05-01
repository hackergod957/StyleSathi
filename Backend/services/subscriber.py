from dotenv import load_dotenv
import os
import requests 
from uuid import uuid4
from supabase import create_client , Client
from core.AppException import AppException
load_dotenv()
import logging
from datetime import datetime, timedelta , timezone

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL") 
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") 
KHALTI_LIVE_SECRET_KEY = os.getenv("KHALTI_LIVE_SECRET_KEY")
KHALTI_BASE_URL = os.getenv("KHALTI_BASE_URL")


supabase : Client = create_client(SUPABASE_PROJECT_URL,SUPABASE_SERVICE_KEY)

model = {  
    "plans": [
        {
                "id": "basic",
                "name": "Basic",
                "order": 1,
                "price": {
                    "amount": 49,
                    "currency": "NPR"
                },
                "days": 30,
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
                    "currency": "NPR"
                },
                "days": 30,
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
                    "currency": "NPR"
                },
                "days": 30,
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

def getPlans():
    return model


def getPlan(id):
    for plan in model["plans"]:
        if plan["id"] == id:
            return  plan


def InitiateSubscribe(plan,user_id):

    required_fields = ["pidx", "payment_url"]
    order_id = f"sub_{uuid4()}"

    logging.info(f"Payment started: {order_id} user={user_id}")
    data = initiate_payment(plan,order_id)


    if not all(field in data for field in required_fields):
        logging.error(f"Gateway failure: order={order_id}")
        raise AppException("Invalid gateway response", 502)
    

    payment_record(plan,order_id,user_id,data)

    return {
        "payment_url" : data["payment_url"],
        "pidx" : data["pidx"],
    }

def initiate_payment(plan,order_id):
    
    
    header = {
        "Authorization" : f"key {KHALTI_LIVE_SECRET_KEY}"
    }

    payload = {
        "return_url" : "https://yourfrontend.com/payment-success",
        "website_url" : "https://yourfrontend.com",
        "amount" : plan["price"]["amount"]  * 100,
        "purchase_order_id" : order_id,
        "purchase_order_name" : plan["name"]
    }

    try:
        response = requests.post(
            KHALTI_BASE_URL + "epayment/initiate/",
            json=payload,
            headers=header,
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Gateway failure: order={order_id}, error={str(e)}")
        raise AppException("Gateway unreachable", 502)


    if not response.ok:

        logging.error(f"Khalti failed: order={order_id}, status={response.status_code}")
        raise AppException(
            f"Khalti error: {response.status_code}",
            502
        )
    
    try:
        data = response.json()
    except ValueError:
        logging.error(f"Gateway failure: order={order_id}, status={response.status_code}")
        raise AppException("Invalid JSON from gateway", 502)
    
    return data



def payment_record(plan,order_id,user_id,data):
     
    try:
        supabase.table("payments").insert({
            "user_id" : user_id,
            "order_id" : order_id,
            "pidx" : data["pidx"],
            "amount": plan["price"]["amount"],
            "currency" : plan["price"]["currency"],
            "status" : "pending",
            "type" : plan["id"],
            "gateway" : "Khalti"
        }).execute()

    except Exception as e:
        logging.error(f"DB insert failed: {str(e)} , {order_id} , {user_id}")
        raise AppException("DB error while saving payment", 500)
    

def verifyPayment(pidx):
    try:
        payment = supabase.table("payments").select("*").eq("pidx",pidx).single().execute()
  
    except Exception:
        raise AppException("Payment not found", 404)
    
    plan = getPlan(payment.data["type"])


    if not plan:
        raise AppException("Invalid plan", 400)

    payment = paymentFormatCheck(payment,plan)

    if payment.data["status"] in ["completed","processing"]:
        return "Already handled"


    res = supabase.table("payments").update({
    "status": "processing"
    }).eq("pidx", pidx).execute()

    if not res.data:
        return "Already handled"


    
    
    
    try:
        response = requests.post(
            KHALTI_BASE_URL+"epayment/lookup/",
            json={"pidx":pidx},
            headers={
                "Authorization" : f"key {KHALTI_LIVE_SECRET_KEY}"
            },
            timeout=10
        )
    
    
    except requests.exceptions.RequestException:
    
        supabase.table("payments").update({
            "status": "pending"
        }).eq("pidx", pidx).execute()

        raise AppException("Gateway unreachable", 502)


    if not response.ok:
        supabase.table("payments").update({
            "status": "pending"
        }).eq("pidx", pidx).execute()

        raise AppException("Khalti lookup failed", 502)

    data = response.json()
    
    if data.get("pidx") != pidx:
        raise AppException("Pidx mismatch", 400)
    
    if data.get("total_amount") != payment.data["amount"] * 100:
        raise AppException("Amount mismatch from gateway", 400)

    status = data.get("status")

    if not status:
        raise AppException("Invalid Khalti response", 502)
    
      
    status = updateStatus(status,payment,pidx,plan)

   
    

    return status

def updateStatus(status,payment,pidx,plan):

    if not isinstance(status, str):
        raise AppException("Invalid status type", 502)

    status = status.strip().lower()

    if status == "completed":

        supabase.table("payments").update({
            "status" : "completed"
        }).eq("pidx",pidx).execute()

        expiry = datetime.now(timezone.utc) + timedelta(days=plan["days"]) 


        res = supabase.table("users").update({
            "subscription_type" : payment.data["type"],
            "subscription_status" : "active",
            "subscription_expiry" : expiry.isoformat()
        }).eq("id" , payment.data["user_id"]).execute()

        if not res.data:
            raise AppException("User update failed", 500)
        
        logging.info(f"Payment completed: {pidx} user={payment.data['user_id']}")
        
    elif status in ["user canceled","expired","failed"]:
        supabase.table("payments").update({
            "status" : "failed"
        }).eq("pidx",pidx).execute()

    elif status == "pending":
        supabase.table("payments").update({
        "status" : "pending"
    }).eq("pidx",pidx).execute()

    else: 
        raise AppException("Unknown payment status", 502)    

    return status

def paymentFormatCheck(payment,plan):
    required = ["amount", "type", "user_id", "status", "pidx"]

    if not all(k in payment.data for k in required):
        raise AppException("Corrupted payment record", 500)

    if payment.data["amount"] != plan["price"]["amount"]:
        raise AppException("Payment mismatch", 400)
    
    return payment