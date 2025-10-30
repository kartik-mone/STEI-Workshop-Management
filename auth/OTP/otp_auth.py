import random
import re
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database.db import get_db_connection
from auth.jwt.jwt_auth import create_access_token
from auth.OTP.send_email import send_email

router = APIRouter(prefix="/auth", tags=["OTP Auth"])

# In-memory OTP store
otp_store = {}
OTP_EXPIRY_SECONDS = 600  # 10 minutes


class SendOtpRequest(BaseModel):
    identifier: str  # Can be email or phone


class VerifyOtpRequest(BaseModel):
    identifier: str
    otp: str


# -----------------------
# SEND OTP
# -----------------------
@router.post("/student/send_otp")
def send_otp(payload: SendOtpRequest, conn=Depends(get_db_connection)):
    identifier = payload.identifier.strip()
    otp = str(random.randint(100000, 999999))
    timestamp = time.time()

    # Detect email vs phone
    is_email = re.match(r"[^@]+@[^@]+\.[^@]+", identifier)
    is_phone = re.match(r"^\+?\d{10,13}$", identifier)

    if not (is_email or is_phone):
        raise HTTPException(status_code=400, detail="Invalid identifier. Enter a valid email or phone number.")

    with conn.cursor() as cursor:
        if is_email:
            cursor.execute("SELECT student_id FROM students WHERE email=%s", (identifier,))
        else:
            cursor.execute("SELECT student_id FROM students WHERE phone=%s", (identifier,))
        student = cursor.fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found with provided identifier.")

    otp_store[identifier] = {"otp": otp, "timestamp": timestamp}

    if is_email:
        send_email(
            to_email=identifier,
            subject="Your OTP Code | SETI",
            message=f"Your OTP code is {otp}. It is valid for 10 minutes."
        )
        return {"message": f"OTP sent to {identifier}"}
    else:
        print(f"[DEBUG] OTP for {identifier}: {otp}")
        return {"message": f"OTP generated for phone {identifier} (check console)"}


# -----------------------
# VERIFY OTP
# -----------------------
@router.post("/student/verify_otp")
def verify_otp(payload: VerifyOtpRequest, conn=Depends(get_db_connection)):
    identifier = payload.identifier.strip()

    if identifier not in otp_store:
        raise HTTPException(status_code=400, detail="OTP not found or expired")

    record = otp_store[identifier]
    otp = record["otp"]
    timestamp = record["timestamp"]

    # Check expiration
    if time.time() - timestamp > OTP_EXPIRY_SECONDS:
        del otp_store[identifier]
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")

    # Check match
    if payload.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Determine if email or phone
    is_email = re.match(r"[^@]+@[^@]+\.[^@]+", identifier)

    with conn.cursor() as cursor:
        if is_email:
            cursor.execute("SELECT student_id FROM students WHERE email=%s", (identifier,))
        else:
            cursor.execute("SELECT student_id FROM students WHERE phone=%s", (identifier,))
        student = cursor.fetchone()

    del otp_store[identifier]

    token = create_access_token({"student_id": student["student_id"], "role": "student"})
    return {"message": "OTP verified successfully", "token": token}
