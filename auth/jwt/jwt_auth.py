from fastapi import Depends, HTTPException, Header
import jwt
from datetime import datetime, timedelta
from database.db import get_db_connection

SECRET_KEY = "SUPER-SECRET-KEY"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_minutes: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes) if expires_minutes else datetime.utcnow() + timedelta(hours=12)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def cleanup_blacklist(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, token FROM blacklisted_tokens")
        tokens = cursor.fetchall()
        for row in tokens:
            try:
                jwt.decode(row["token"], SECRET_KEY, algorithms=[ALGORITHM])
            except jwt.ExpiredSignatureError:
                cursor.execute("DELETE FROM blacklisted_tokens WHERE id=%s", (row["id"],))
                conn.commit()


def is_token_blacklisted(token: str, conn):
    cleanup_blacklist(conn)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM blacklisted_tokens WHERE token=%s", (token,))
        return cursor.fetchone() is not None


def extract_token(auth_header: str):
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    else:
        return auth_header.strip()



#  Student Token Validation + Profile Return
def require_student(Authorization: str = Header(None), conn=Depends(get_db_connection)):
    token = extract_token(Authorization)
    if is_token_blacklisted(token, conn):
        raise HTTPException(status_code=401, detail="Token has been logged out. Please login again.")

    decoded = decode_token(token)
    if decoded.get("role") != "student":
        raise HTTPException(status_code=403, detail="Only students allowed")

    with conn.cursor() as cursor:
        cursor.execute("SELECT student_id, first_name, last_name, phone, email FROM students WHERE student_id=%s",
                       (decoded["student_id"],))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student


#  Admin Token Validation + Profile Return
def require_admin(Authorization: str = Header(None), conn=Depends(get_db_connection)):
    token = extract_token(Authorization)
    if is_token_blacklisted(token, conn):
        raise HTTPException(status_code=401, detail="Token has been logged out. Please login again.")

    decoded = decode_token(token)
    if decoded.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins allowed")

    with conn.cursor() as cursor:
        cursor.execute("SELECT admin_id, first_name, last_name, email FROM admins WHERE admin_id=%s",
                       (decoded["admin_id"],))
        admin = cursor.fetchone()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return admin
