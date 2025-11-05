from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student
from typing import Optional, List


clarity_call_router = APIRouter(
    prefix="/student/clarity_call",
    tags=["Clarity Call"]
)


#   GET → Clarity Call Status  OR Fetch clarity call details
#  -----------------------------
@clarity_call_router.get("/clarity_call_status")
def get_clarity_call_status(student=Depends(require_student), conn=Depends(get_db_connection)):
    if not student:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    student_id = student["student_id"]

    query = """
        SELECT call_status
        FROM clarity_calls
        WHERE student_id = %s
        ORDER BY scheduled_date DESC
        
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (student_id,))
        records = cursor.fetchall()

    if not records:
        return {"clarity_call_status": "Not Scheduled"}

    return {
        "clarity_call_status": records[0]["call_status"],
        # "scheduled_date": str(records[0]["scheduled_date"]) if records[0]["scheduled_date"] else None,
        # "mentor_name": records[0]["mentor_name"]
    }



#  GET → Call History
#  -----------------------------------------

@clarity_call_router.get("/history")
def clarity_call_history(
    student=Depends(require_student),
    conn=Depends(get_db_connection)
):
    student_id = student["student_id"]

    query = """
        SELECT id, mentor_name, call_status, scheduled_date, notes
        FROM clarity_calls
        WHERE student_id = %s
        ORDER BY scheduled_date DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()

    return {"history": rows or []}
