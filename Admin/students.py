from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_admin   


students_router_admin = APIRouter( prefix="/admin/students", tags=["Students (Admin)"])


# Pydantic Models 
# -----------------------------------------

class StudentBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    password: str
    confirm_password: str
    email_consent: Optional[bool] = False
    profession: Literal['student', 'employee', 'other'] = 'student'
    designation: Optional[str] = None
    gender: Literal['male', 'female', 'other'] = 'male'


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email_consent: Optional[bool] = None
    profession: Optional[Literal['student', 'employee', 'other']] = None
    designation: Optional[str] = None
    gender: Optional[Literal['male', 'female', 'other']] = None


# Register student 
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
                (first_name, last_name, email, phone, address, password, email_consent, profession, designation, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                student.first_name,
                student.last_name,
                student.email,
                student.phone,
                student.address,
                student.password,        
                student.email_consent,
                student.profession,
                student.designation,
                student.gender
            ))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Student registered successfully by Admin {user['admin_id']}"}


# GET → Get all students with workshop & batch info 
# -----------------------------------------
@students_router_admin.get("/")
async def get_students(conn=Depends(get_db_connection),
                       user=Depends(require_admin)):
    query = """
        SELECT 
            s.student_id, s.first_name, s.last_name, s.email, s.phone, s.address,
            s.password, s.email_consent, s.profession, s.designation, s.gender,
            s.created_at, s.updated_at,
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


# GET → Get specific student by ID 
# -----------------------------------------

@students_router_admin.get("/{student_id}")
async def get_student(student_id: int,
                      conn=Depends(get_db_connection),
                      user=Depends(require_admin)):
    query = """
        SELECT 
            s.student_id, s.first_name, s.last_name, s.email, s.phone, s.address,
            s.password, s.email_consent, s.profession, s.designation, s.gender, s.status,
            s.created_at, s.updated_at,
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


# PUT → Update student dynamically 
# -----------------------------------------

@students_router_admin.put("/update/{student_id}")
async def update_student(student_id: int,
                         student: StudentUpdate,
                         conn=Depends(get_db_connection),
                         user=Depends(require_admin)):
    data = student.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    allowed_fields = ["first_name", "last_name", "phone", "address",
                      "email_consent", "profession", "designation", "gender"]
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


# DELETE → Delete student
# -------------------------

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




#  POST → Create Student Assignments
# ----------------------------------

@students_router_admin.post("/create_assignments")
def create_assignment(data: dict, admin=Depends(require_admin), conn=Depends(get_db_connection)):
    
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    required_fields = ["student_id", "assignment_title", "description"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    student_id = data["student_id"]
    title = data["assignment_title"]
    description = data["description"]
    status = data.get("status", "Assigned")

    # Check student exists
    with conn.cursor() as cursor:
        cursor.execute("SELECT student_id, first_name, last_name FROM students WHERE student_id=%s", (student_id,))
        student = cursor.fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Insert assignment
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO student_assignments (student_id, assignment_title, description, status)
            VALUES (%s, %s, %s, %s)
        """, (student_id, title, description, status))

        conn.commit()

    return {
        "message": "Assignment created successfully",
        "student": {
            "id": student["student_id"],
            "name": f"{student['first_name']} {student['last_name']}"
        },
        "assignment": {
            "title": title,
            "status": status
        }
    }




# DELETE → Remove incomplete student
# -----------------------------------------
@students_router_admin.delete("/delete_incomplete/{student_id}")
def delete_incomplete_student(
    student_id: int,
    admin=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM students WHERE student_id=%s AND profile_completed=0",
            (student_id,)
        )
        affected = cursor.rowcount
        conn.commit()

    if affected == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found or profile is completed"
        )

    return {"message": f"Incomplete profile student {student_id} deleted successfully"}

