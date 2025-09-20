from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from db import get_db_connection
from auth import require_admin   # Protect with admin token

students_router_admin = APIRouter(
    prefix="/students",
    tags=["Students (Admin)"]
)


# ---------------- Pydantic Models ----------------
class StudentBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    password: str
    confirm_password: str
    email_consent: Optional[bool] = False


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email_consent: Optional[bool] = None


# ---------------- ADMIN ROUTES ----------------

# Register student (Admin only)
@students_router_admin.post("/register")
async def register_student(student: StudentBase,
                           conn=Depends(get_db_connection),
                           user=Depends(require_admin)):   # Admin required
    if student.password != student.confirm_password:
        raise HTTPException(status_code=400, detail="Password and Confirm Password do not match")

    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO students 
                (first_name, last_name, email, phone, address, password, email_consent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                student.first_name,
                student.last_name,
                student.email,
                student.phone,
                student.address,
                student.password,         # ⚠️ should be hashed in real app
                student.email_consent
            ))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Student registered successfully by Admin {user['admin_id']}"}


# Get all students with workshop & batch info (Admin only)
@students_router_admin.get("/")
async def get_students(conn=Depends(get_db_connection),
                       user=Depends(require_admin)):
    query = """
        SELECT 
            s.student_id, s.first_name, s.last_name, s.email, s.phone, s.address,
            s.password, s.email_consent, s.created_at, s.updated_at,
            se.enrollment_id, se.status AS enrollment_status, se.enrollment_date,
            b.id AS batch_id, b.batch_name, b.status AS batch_status,
            w.workshop_id, w.name AS workshop_name
        FROM students s
        LEFT JOIN student_enrollments se ON s.student_id = se.student_id
        LEFT JOIN batches b ON se.batch_id = b.id
        LEFT JOIN workshops w ON se.workshop_id = w.workshop_id
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            students = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return students if students else {"message": "No students found"}


# Get specific student by ID (Admin only)
@students_router_admin.get("/{student_id}")
async def get_student(student_id: int,
                      conn=Depends(get_db_connection),
                      user=Depends(require_admin)):
    query = """
        SELECT 
            s.student_id, s.first_name, s.last_name, s.email, s.phone, s.address,
            s.password, s.email_consent, s.created_at, s.updated_at,
            se.enrollment_id, se.status AS enrollment_status, se.enrollment_date,
            b.id AS batch_id, b.batch_name, b.status AS batch_status,
            w.workshop_id, w.name AS workshop_name
        FROM students s
        LEFT JOIN student_enrollments se ON s.student_id = se.student_id
        LEFT JOIN batches b ON se.batch_id = b.id
        LEFT JOIN workshops w ON se.workshop_id = w.workshop_id
        WHERE s.student_id = %s
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (student_id,))
            student = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


# Update student dynamically (Admin only)
@students_router_admin.put("/update/{student_id}")
async def update_student(student_id: int,
                         student: StudentUpdate,
                         conn=Depends(get_db_connection),
                         user=Depends(require_admin)):
    data = student.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    allowed_fields = ["first_name", "last_name", "phone", "address", "email_consent"]
    fields = []
    values = []

    for key in allowed_fields:
        if key in data:
            fields.append(f"{key}=%s")
            values.append(data[key])

    query = f"UPDATE students SET {', '.join(fields)} WHERE student_id=%s"
    values.append(student_id)

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(values))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Student {student_id} updated successfully by Admin {user['admin_id']}"}


# Delete student (Admin only)
@students_router_admin.delete("/delete/{student_id}")
async def delete_student(student_id: int,
                         conn=Depends(get_db_connection),
                         user=Depends(require_admin)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Student {student_id} deleted successfully by Admin {user['admin_id']}"}
