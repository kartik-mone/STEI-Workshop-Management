# auth/oauth_google.py
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from database.db import get_db_connection
from auth.jwt.jwt_auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Google"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # set this in your .env for production


class GoogleLoginRequest(BaseModel):
    id_token: str  # Google ID token obtained from client or Postman


@router.post("/google/login")
def google_login(payload: GoogleLoginRequest, conn=Depends(get_db_connection)):
    # 1) Verify token with Google
    try:
        # This will raise ValueError on invalid token
        ticket = id_token.verify_oauth2_token(payload.id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    # 2) Extract profile info
    email = ticket.get("email")
    sub = ticket.get("sub")  # Google's unique user id
    first_name = ticket.get("given_name") or ""
    last_name = ticket.get("family_name") or ""

    if not email:
        raise HTTPException(status_code=400, detail="Google token did not contain an email")

    # 3) Upsert into students table (students only)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        student = cursor.fetchone()

        if not student:
            # Insert new student. Password left empty (or you can generate random).
            cursor.execute(
                """INSERT INTO students
                   (first_name, last_name, email, password, google_id)
                   VALUES (%s, %s, %s, %s, %s)""",
                (first_name, last_name, email, "", sub)
            )
            conn.commit()
            # fetch inserted student
            cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
            student = cursor.fetchone()
        else:
            # If student exists but google_id not set, update it
            if not student.get("google_id"):
                cursor.execute("UPDATE students SET google_id=%s WHERE student_id=%s", (sub, student["student_id"]))
                conn.commit()
                student["google_id"] = sub

    # 4) Issue JWT token for student
    token_payload = {"student_id": student["student_id"], "role": "student"}
    # If your create_access_token supports expires_minutes=None => never expires, pass None
    token = create_access_token(token_payload, expires_minutes=None)

    return {"message": "Google login successful", "token": token}
