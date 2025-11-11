from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student

update_student_router = APIRouter(prefix="/auth", tags=["Auth"])



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


# Helper — check profile completion
# -------------------------

def is_profile_complete(s: dict):
    required_fields = [
        "first_name", "last_name", "email", "phone",
        "address", "profession", "designation", "gender"
    ]
    return all(s.get(f) not in (None, "", False) for f in required_fields)


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

    # Prevent duplicate email
    if "email" in data:
        with conn.cursor() as cursor:
            cursor.execute("SELECT student_id FROM students WHERE email=%s", (data["email"],))
            existing = cursor.fetchone()
            if existing and existing["student_id"] != student_id:
                raise HTTPException(status_code=400, detail="Email already in use")

    # Build update SQL dynamically
    set_parts = [f"{field}=%s" for field in data.keys()]
    values = list(data.values())
    values.append(student_id)

    update_query = f"UPDATE students SET {', '.join(set_parts)} WHERE student_id=%s"

    with conn.cursor() as cursor:
        cursor.execute(update_query, tuple(values))
        conn.commit()

        # Fetch updated row
        cursor.execute(
            """
            SELECT first_name, last_name, email, phone, address,
                   profession, designation, gender
            FROM students WHERE student_id=%s
            """,
            (student_id,)
        )
        updated = cursor.fetchone()

    if not updated:
        raise HTTPException(status_code=404, detail="Student not found after update")

    # Determine profile completion
    profile_done = is_profile_complete(updated)

    # Update DB
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE students SET profile_completed=%s WHERE student_id=%s",
            (profile_done, student_id)
        )
        conn.commit()

    return {
        "message": "Profile updated successfully",
        "profile_completed": bool(profile_done),
        "student": updated
    }
