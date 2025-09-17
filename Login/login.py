from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from db import get_db_connection

router = APIRouter()
SECRET_KEY = "SUPER-SECRET-KEY"
ALGORITHM = "HS256"

#  Request model 
class LoginRequest(BaseModel):
    phone: str
    password: str


#  Login Route 
@router.post("/login")
def student_login(data: LoginRequest, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE phone=%s", (data.phone,))
    student = cursor.fetchone()
    cursor.close()  

    if not student or student["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    # Generate JWT
    token = jwt.encode(
        {
            "student_id": student["student_id"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful",
        "token": token,
        "student": {
            "student_id": student["student_id"],
            "phone": student["phone"]
        }
    }


#  Profile Route 
@router.get("/profile")
def student_profile(Authorization: str = Header(None), conn=Depends(get_db_connection)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token is missing")

    token = Authorization
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id = decoded["student_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    student = cursor.fetchone()
    cursor.close()   

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "student_id": student["student_id"],
        "first_name": student.get("first_name", ""),
        "last_name": student.get("last_name", ""),
        "email": student.get("email", ""),
        "phone": student["phone"],
        "address": student.get("address", "")
    }
