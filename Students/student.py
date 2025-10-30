from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from database.db import get_db_connection
from auth.jwt.password_auth import hash_password
from auth.jwt.jwt_auth import require_student

students_router = APIRouter(prefix="/student", tags=["Students"])

class StudentBase(BaseModel):
    # Required fields
    first_name: str
    email: EmailStr
    phone: str
    password: str
    confirm_password: str

    # Optional fields
    last_name: Optional[str] = None
    address: Optional[str] = None
    email_consent: Optional[bool] = False
    profession: Optional[Literal['student', 'employee', 'other']] = 'student'
    designation: Optional[str] = None
    gender: Optional[Literal['male', 'female', 'other']] = None


@students_router.post("/register")
async def register_student(student: StudentBase, conn=Depends(get_db_connection)):
    # Password Match Check
    if student.password != student.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check Existing Email
    with conn.cursor() as cursor:
        cursor.execute("SELECT email FROM students WHERE email = %s", (student.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

    # Save Student with Hashed Password
    hashed_password = hash_password(student.password)
    with conn.cursor() as cursor:
        query = """
            INSERT INTO students (
                first_name, last_name, email, phone, address, password,
                email_consent, profession, designation, gender
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                student.first_name,
                student.last_name,
                student.email,
                student.phone,
                student.address,
                hashed_password,
                student.email_consent,
                student.profession,
                student.designation,
                student.gender,
            ),
        )
        conn.commit()

    return {"message": "Student registered successfully"}



@students_router.get("/completion")
def get_profile_completion(student=Depends(require_student), conn=Depends(get_db_connection)):
    student_id = student["student_id"]

    with conn.cursor() as cursor:
        cursor.execute("SELECT first_name, last_name, email, phone, address, profession, designation, gender FROM students WHERE student_id=%s", (student_id,))
        student_data = cursor.fetchone()

    if not student_data:
        raise HTTPException(status_code=404, detail="Student not found")

    total_fields = len(student_data)
    filled_fields = sum(1 for v in student_data.values() if v not in (None, "", False))
    completion_percentage = round((filled_fields / total_fields) * 100, 2)

    return {"student_id": student_id, "completion_percentage": completion_percentage}



@students_router.post("/mark-complete")
def mark_profile_complete(student=Depends(require_student), conn=Depends(get_db_connection)):
    student_id = student["student_id"]

    required_fields = [
        "first_name", "last_name", "email", "phone",
        "address", "profession", "designation", "gender"
    ]

    with conn.cursor() as cursor:
        # Fetch student details
        cursor.execute(
            f"SELECT {', '.join(required_fields)} FROM students WHERE student_id = %s",
            (student_id,)
        )
        student_data = cursor.fetchone()

        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found")

        # Check if all required fields are filled
        missing_fields = [field for field, value in student_data.items() if not value]

        if missing_fields:
            return {
                "message": "Profile is incomplete",
                "missing_fields": missing_fields,
                "profile_completed": False
            }

        # Mark profile as completed
        cursor.execute(
            "UPDATE students SET profile_completed = TRUE WHERE student_id = %s",
            (student_id,)
        )
        conn.commit()

    return {
        "message": "Profile marked as completed successfully",
        "profile_completed": True
    }



@students_router.get("/progress")
def get_profile_progress(student=Depends(require_student), conn=Depends(get_db_connection)):
    student_id = student["student_id"]

    with conn.cursor() as cursor:
        cursor.execute("SELECT first_name, last_name, email, phone, address, profession, designation, gender FROM students WHERE student_id=%s", (student_id,))
        student_data = cursor.fetchone()

    if not student_data:
        raise HTTPException(status_code=404, detail="Student not found")

    progress_data = {}

    for field, value in student_data.items():
        # If the field has a non-empty value, mark it True
        if isinstance(value, str):
            progress_data[field] = bool(value.strip())
        else:
            progress_data[field] = bool(value)

    total = len(progress_data)
    filled = sum(progress_data.values())
    percentage = round((filled / total) * 100, 2)

    return {
        "student_id": student_id,
        "progress_details": progress_data,
        "progress_percentage": percentage
    }


