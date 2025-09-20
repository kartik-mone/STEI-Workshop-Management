from fastapi import APIRouter, Depends, Header, HTTPException
from db import get_db_connection
from auth import require_student, require_admin, SECRET_KEY, ALGORITHM
import jwt

logout_router = APIRouter(prefix="/auth", tags=["Auth"])


# Student Logout
@logout_router.post("/student/logout")
def student_logout(Authorization: str = Header(None),
                   user=Depends(require_student),
                   conn=Depends(get_db_connection)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token is missing")

    token = Authorization.split(" ")[1] if Authorization.startswith("Bearer ") else Authorization

    # Validate token
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("role") != "student":
            raise HTTPException(status_code=403, detail="Not a student token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token already expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Blacklist token
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO blacklisted_tokens (token) VALUES (%s)", (token,))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Student {user['student_id']} logged out successfully"}


# Admin Logout
@logout_router.post("/admin/logout")
def admin_logout(Authorization: str = Header(None),
                 user=Depends(require_admin),
                 conn=Depends(get_db_connection)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token is missing")

    token = Authorization.split(" ")[1] if Authorization.startswith("Bearer ") else Authorization

    # Validate token
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not an admin token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token already expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Blacklist token
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO blacklisted_tokens (token) VALUES (%s)", (token,))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Admin {user['first_name']} logged out successfully"}
