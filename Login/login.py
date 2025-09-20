from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from db import get_db_connection
from auth import require_student, require_admin, SECRET_KEY, ALGORITHM  

router = APIRouter(prefix="/auth", tags=["Auth"])

# Request model
class LoginRequest(BaseModel):
    phone: str
    password: str

class AdminLoginRequest(BaseModel):
    email: str
    password: str

# Student Login
@router.post("/student/login")
def student_login(data: LoginRequest, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE phone=%s", (data.phone,))
    student = cursor.fetchone()
    cursor.close()

    if not student or student["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    token = jwt.encode(
        {
            "student_id": student["student_id"],
            "role": "student",
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Student login successful",
        "token": token
    }


# Student Profile
@router.get("/student/profile")
def student_profile(user=Depends(require_student)):
    """
    Returns student's profile.
    require_student ensures token is valid, not blacklisted, and fetches profile.
    """
    return user


# Admin Login
@router.post("/admin/login")
def admin_login(data: AdminLoginRequest, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE email=%s", (data.email,))
    admin = cursor.fetchone()
    cursor.close()

    if not admin or admin["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = jwt.encode(
        {
            "admin_id": admin["admin_id"],
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Admin login successful",
        "token": token
    }


@router.get("/admin/profile")
def admin_profile(user=Depends(require_admin)):
    """
    Returns admin's profile.
    `require_admin` ensures token is valid, not blacklisted, and fetches profile.
    """
    return user

