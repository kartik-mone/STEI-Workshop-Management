from fastapi import Depends, HTTPException, Header
import jwt
from db import get_db_connection
from datetime import datetime, timezone

SECRET_KEY = "SUPER-SECRET-KEY"
ALGORITHM = "HS256"


# Decode JWT
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Cleanup expired blacklisted tokens
def cleanup_blacklist(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, token FROM blacklisted_tokens")
        tokens = cursor.fetchall()

        for row in tokens:
            try:
                # If token still valid, skip
                jwt.decode(row["token"], SECRET_KEY, algorithms=[ALGORITHM])
            except jwt.ExpiredSignatureError:
                # Token expired → remove from blacklist
                cursor.execute("DELETE FROM blacklisted_tokens WHERE id=%s", (row["id"],))
                conn.commit()


# Check if token is blacklisted
def is_token_blacklisted(token: str, conn):
    cleanup_blacklist(conn)  # auto cleanup before check
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM blacklisted_tokens WHERE token=%s", (token,))
        return cursor.fetchone() is not None


# Require Student (with DB lookup + blacklist check)
def require_student(Authorization: str = Header(None), conn=Depends(get_db_connection)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token is missing")

    token = Authorization.split(" ")[1] if Authorization.startswith("Bearer ") else Authorization

    if is_token_blacklisted(token, conn):
        raise HTTPException(status_code=401, detail="Token has been blacklisted. Please login again.")

    decoded = decode_token(token)

    if decoded.get("role") != "student" or "student_id" not in decoded:
        raise HTTPException(status_code=403, detail="Not authorized as student")

    student_id = decoded["student_id"]

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT student_id, first_name, last_name, email, phone, address FROM students WHERE student_id=%s",
            (student_id,)
        )
        student = cursor.fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


# Require Admin (with DB lookup + blacklist check)
def require_admin(Authorization: str = Header(None), conn=Depends(get_db_connection)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token is missing")

    token = Authorization.split(" ")[1] if Authorization.startswith("Bearer ") else Authorization

    if is_token_blacklisted(token, conn):
        raise HTTPException(status_code=401, detail="Token has been blacklisted. Please login again.")

    decoded = decode_token(token)

    if decoded.get("role") != "admin" or "admin_id" not in decoded:
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    admin_id = decoded["admin_id"]

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT admin_id, first_name, last_name, email, phone FROM admins WHERE admin_id=%s",
            (admin_id,)
        )
        admin = cursor.fetchone()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin
