from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student

update_student_router = APIRouter(prefix="/auth", tags=["Auth"])


# -------------------------
# Update request model
# -------------------------
class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    profession: Optional[Literal["student", "employee", "other"]] = None
    designation: Optional[str] = None
    gender: Optional[Literal["male", "female", "other"]] = None


# -------------------------
# Update endpoint
# -------------------------
@update_student_router.put("/student/update")
def update_student_profile(
    update_data: StudentUpdate,
    student=Depends(require_student),
    conn=Depends(get_db_connection),
):
    student_id = student["student_id"]

    # Filter only provided (non-null) fields
    data = update_data.dict(exclude_unset=True)

    if not data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    # Optional: prevent email change if you don’t allow it
    if "email" in data:
        with conn.cursor() as cursor:
            cursor.execute("SELECT student_id FROM students WHERE email = %s", (data["email"],))
            existing = cursor.fetchone()
            if existing and existing[0] != student_id:
                raise HTTPException(status_code=400, detail="Email already in use")

    # Build SQL dynamically
    set_parts = [f"{field}=%s" for field in data.keys()]
    values = list(data.values())
    values.append(student_id)

    query = f"UPDATE students SET {', '.join(set_parts)} WHERE student_id=%s"

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, tuple(values))
        conn.commit()

        cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
        updated_student = cursor.fetchone()

    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found after update")

    return {
        "message": "Profile updated successfully",
        "student": updated_student
    }
