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



# Helper Function's 
# -----------------------------------------

def is_profile_complete(student_dict: dict) -> bool:
    required = [
        "first_name", "last_name", "email", "phone",
        "address", "profession", "designation", "gender"
    ]
    return all(student_dict.get(f) not in (None, "", False) for f in required)


def recalc_profile_completion(student_id, conn):
    required = [
        "first_name", "last_name", "email", "phone",
        "address", "profession", "designation", "gender"
    ]

    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT {', '.join(required)} FROM students WHERE student_id=%s",
            (student_id,)
        )
        data = cursor.fetchone()

    profile_complete = is_profile_complete(data)

    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE students SET profile_completed=%s WHERE student_id=%s",
            (profile_complete, student_id)
        )
        conn.commit()

    return profile_complete



# Student Registration
# -----------------------------------------
@students_router.post("/register")
async def register_student(student: StudentBase, conn=Depends(get_db_connection)):
    if student.password != student.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    with conn.cursor() as cursor:
        cursor.execute("SELECT email FROM students WHERE email=%s", (student.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(student.password)

    student_data = {
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
        "phone": student.phone,
        "address": student.address,
        "profession": student.profession,
        "designation": student.designation,
        "gender": student.gender,
    }

    profile_complete = is_profile_complete(student_data)

    with conn.cursor() as cursor:
        query = """
            INSERT INTO students (
                first_name, last_name, email, phone, address, password,
                email_consent, profession, designation, gender, profile_completed
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                profile_complete
            ),
        )
        conn.commit()

    return {
        "message": "Student registered successfully",
    }




# GET Profile Completion Percentage
# -----------------------------------------
@students_router.get("/completion")
def get_profile_completion(student=Depends(require_student), conn=Depends(get_db_connection)):
    
    student_id = student["student_id"]

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT first_name, last_name, email, phone, address, profession, designation, gender "
            "FROM students WHERE student_id=%s",
            (student_id,)
        )
        data = cursor.fetchone()

    if not data:
        raise HTTPException(status_code=404, detail="Student not found")

    total = len(data)
    filled = sum(1 for v in data.values() if v not in (None, "", False))
    pct = round((filled / total) * 100, 2)

    return {
        "student_id": student_id,
        "completion_percentage": pct
    }


# GET Progress Details
# -----------------------------------------
@students_router.get("/progress")
def get_profile_progress(student=Depends(require_student), conn=Depends(get_db_connection)):
    student_id = student["student_id"]

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT first_name, last_name, email, phone, address, profession, designation, gender "
            "FROM students WHERE student_id=%s",
            (student_id,)
        )
        data = cursor.fetchone()

    if not data:
        raise HTTPException(status_code=404, detail="Student not found")

    progress = {}
    for field, value in data.items():
        progress[field] = bool(value and str(value).strip())

    total = len(progress)
    filled = sum(progress.values())
    pct = round((filled / total) * 100, 2)

    return {
        "student_id": student_id,
        "progress_details": progress,
        "progress_percentage": pct
    }


#  Clean In Process Assignment 
# -----------------------------

@students_router.delete("/cleanup_Assignment")
def cleanup_inprogress_data(student=Depends(require_student), conn=Depends(get_db_connection)):
    if not student:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    student_id = student["student_id"]

    with conn.cursor() as cursor:
        # Remove in-progress assignments
        cursor.execute("""
            DELETE FROM student_assignments 
            WHERE student_id = %s AND status IN ('In Progress')
        """, (student_id,))

    conn.commit()
    return {"message": f"Removed all in-progress assignment data successfully from {student['first_name']}."}