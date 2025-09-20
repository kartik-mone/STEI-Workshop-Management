from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from db import get_db_connection

students_router = APIRouter(prefix="/students", tags=["Students"])

class StudentBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    password: str
    confirm_password: str
    email_consent: Optional[bool] = False


# Register student
@students_router.post("/register")
async def register_student(student: StudentBase, conn=Depends(get_db_connection)):
    if student.password != student.confirm_password:
        raise HTTPException(status_code=400, detail="Password and Confirm Password do not match")

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
            student.password,
            student.email_consent
        ))
        conn.commit()

    return {"message": "Student registered successfully"}
