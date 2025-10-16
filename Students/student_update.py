from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from db import get_db_connection
from auth import require_student

update_student_router = APIRouter(prefix="/auth", tags=["Auth"])

# Request model for student update
class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    email: EmailStr | None = None

# Update student profile
@update_student_router.put("/student/update")
async def update_student_profile(
    data: StudentUpdate,
    user=Depends(require_student),
    conn=Depends(get_db_connection)
):
    student_id = user["student_id"]

    update_data = data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    allowed_fields = ["first_name", "last_name", "phone", "address", "email", "profession", "designation", "gender"]
    fields = []
    values = []

    for key in allowed_fields:
        if key in update_data:
            fields.append(f"{key}=%s")
            values.append(update_data[key])

    if not fields:
        raise HTTPException(status_code=400, detail="No allowed fields provided")

    values.append(student_id)  # for WHERE clause

    query = f"UPDATE students SET {', '.join(fields)} WHERE student_id=%s"

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(values))
            conn.commit()

            # Fetch updated profile
            cursor.execute("SELECT student_id, first_name, last_name, phone, address, " 
                            "email, profession, designation, gender FROM students WHERE student_id=%s", (student_id,))
            updated_student = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Profile updated successfully",
        "student": updated_student
    }
