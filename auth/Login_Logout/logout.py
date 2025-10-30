from fastapi import APIRouter, Depends, Header, HTTPException
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student, require_admin, extract_token
from auth.jwt.jwt_auth import SECRET_KEY, ALGORITHM  

router = APIRouter(prefix="/auth", tags=["Auth"])


# Student Logout
@router.post("/student/logout")
def student_logout(
    Authorization: str = Header(None),
    user=Depends(require_student),
    conn=Depends(get_db_connection)
):
    token = extract_token(Authorization)

    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO blacklisted_tokens (token) VALUES (%s)", (token,))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": f"Student ID {user['student_id']} logged out successfully"}


# Admin Logout
@router.post("/admin/logout")
def admin_logout(
    Authorization: str = Header(None),
    user=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    token = extract_token(Authorization)

    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO blacklisted_tokens (token) VALUES (%s)", (token,))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": f"Admin ID {user['admin_id']} logged out successfully"}
