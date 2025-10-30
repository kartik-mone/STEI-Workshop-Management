from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from database.db import get_db_connection
from auth.jwt.password_auth import verify_password, hash_password

from auth.jwt.jwt_auth import create_access_token, require_admin, require_student


router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    phone: str
    password: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/student/login")
def student_login(payload: LoginRequest, conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM students WHERE phone=%s", (payload.phone,))
        student = cursor.fetchone()

    if not student:
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    stored_password = student["password"]

    # If hashed with bcrypt
    if stored_password.startswith("$2b$"):
        valid = verify_password(payload.password, stored_password)
    else:
        valid = payload.password == stored_password
        if valid:
            # Auto-upgrade plain password to bcrypt
            new_hash = hash_password(payload.password)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE students SET password=%s WHERE student_id=%s",
                    (new_hash, student["student_id"])
                )
                conn.commit()

    if not valid:
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    token_data = {"student_id": student["student_id"], "role": "student"}
    token = create_access_token(token_data)

    return {"message": "Student login successful", "token": token}

@router.get("/student/profile")
def student_profile(user=Depends(require_student), conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT student_id, first_name, last_name FROM students WHERE student_id=%s",
            (user["student_id"],)
        )
        student = cursor.fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.post("/admin/login")
def admin_login(payload: AdminLoginRequest, conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM admins WHERE email=%s", (payload.email,))
        admin = cursor.fetchone()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    stored_password = admin["password"]

    if stored_password.startswith("$2b$"):
        valid = verify_password(payload.password, stored_password)
    else:
        valid = payload.password == stored_password

    if not valid:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token_data = {"admin_id": admin["admin_id"], "role": "admin"}
    token = create_access_token(token_data)

    return {"message": "Admin login successful", "token": token}


@router.get("/admin/profile")
def admin_profile(user=Depends(require_admin), conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT admin_id, first_name, last_name FROM admins WHERE admin_id=%s",
            (user["admin_id"],)
        )
        admin = cursor.fetchone()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin



