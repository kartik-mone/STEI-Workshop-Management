from fastapi import APIRouter, Depends, HTTPException
from db import get_db_connection
from auth import require_student  

enrollments_router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# Enroll in workshop + batch (Student only)
@enrollments_router.post("/enroll/{workshop_id}/{batch_id}")
async def enroll_student(workshop_id: int, batch_id: int,
                         user=Depends(require_student),
                         conn=Depends(get_db_connection)):
    student_id = user["student_id"]

    with conn.cursor() as cursor:
        # Fetch student's first_name
        cursor.execute("SELECT first_name FROM students WHERE student_id=%s", (student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Fetch workshop status
        cursor.execute("SELECT name, status FROM workshops WHERE workshop_id=%s", (workshop_id,))
        workshop = cursor.fetchone()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")

        # Fetch batch status
        cursor.execute("SELECT batch_name, status FROM batches WHERE id=%s", (batch_id,))
        batch = cursor.fetchone()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        # Check enrollment eligibility
        if workshop["status"] in ("Completed", "Cancelled"):
            raise HTTPException(status_code=400, detail=f"Cannot enroll: Workshop is {workshop['status']}")
        if batch["status"] in ("Completed", "Cancelled"):
            raise HTTPException(status_code=400, detail=f"Cannot enroll: Batch is {batch['status']}")

        # Decide enrollment status
        if workshop["status"] == "Active" and batch["status"] == "Active":
            enrollment_status = "Active"
        elif workshop["status"] == "Upcoming" and batch["status"] == "Upcoming":
            enrollment_status = "Upcoming"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot enroll: Workshop is {workshop['status']} and Batch is {batch['status']}"
            )

        # Check if already enrolled
        cursor.execute(
            """
            SELECT * FROM student_enrollments
            WHERE student_id=%s AND workshop_id=%s AND batch_id=%s
            """,
            (student_id, workshop_id, batch_id)
        )
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this workshop/batch")

        # Insert enrollment
        try:
            cursor.execute(
                """
                INSERT INTO student_enrollments 
                (student_id, workshop_id, batch_id, status, enrollment_date) 
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (student_id, workshop_id, batch_id, enrollment_status)
            )
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")

    return {
        "message": f"Student {student['first_name']} enrolled in {workshop['name']} ({batch['batch_name']})",
        "status": enrollment_status
    }


# Get current enrollments (Student only)
@enrollments_router.get("/my-enrollments")
async def my_enrollments(user=Depends(require_student),
                         conn=Depends(get_db_connection)):
    student_id = user["student_id"]

    query = """
        SELECT 
            w.name AS workshop_name, 
            b.batch_name, 
            se.status, 
            se.enrollment_date
        FROM student_enrollments se
        JOIN workshops w ON se.workshop_id = w.workshop_id
        JOIN batches b ON se.batch_id = b.id
        WHERE se.student_id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()

    return rows if rows else {"message": "No enrollments found"}