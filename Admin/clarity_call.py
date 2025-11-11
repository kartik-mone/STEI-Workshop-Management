from fastapi import APIRouter, HTTPException, Depends
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_admin   

students_router_admin = APIRouter(
    prefix="/admin/clarity_call",
    tags=["Clarity Calls (Admin)"]
)


# POST → Schedule Clarity Call
@students_router_admin.post("/create")
def create_clarity_call(data: dict, admin=Depends(require_admin), conn=Depends(get_db_connection)):

    required_fields = ["student_id", "mentor_name", "call_status", "scheduled_date"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    student_id = data["student_id"]
    mentor_name = data["mentor_name"]
    call_status = data["call_status"]
    scheduled_date = data["scheduled_date"]
    note = data.get("note")

    # Check student exists
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT student_id, first_name, last_name FROM students WHERE student_id=%s",
            (student_id,)
        )
        student = cursor.fetchone()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Insert clarity call
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO clarity_calls (student_id, mentor_name, call_status, scheduled_date, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_id, mentor_name, call_status, scheduled_date, note))
        conn.commit()

    return {
        "message": "Clarity call scheduled",
        "student": {
            "id": student["student_id"],
            "name": f"{student['first_name']} {student['last_name']}"
        },
        "call": {
            "status": call_status,
            "scheduled_date": scheduled_date,
            "mentor_name": mentor_name
        }
    }



# PUT → Update Clarity Call
@students_router_admin.put("/update/{call_id}")
def update_clarity_call(
    call_id: int,
    data: dict,
    admin=Depends(require_admin),
    conn=Depends(get_db_connection)
):

    allowed_fields = ["mentor_name", "call_status", "scheduled_date", "notes"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM clarity_calls WHERE id=%s", (call_id,))
        record = cursor.fetchone()

    if not record:
        raise HTTPException(status_code=404, detail="Clarity Call entry not found")

    set_parts = ", ".join([f"{field}=%s" for field in update_data.keys()])
    values = list(update_data.values())
    values.append(call_id)

    query = f"UPDATE clarity_calls SET {set_parts} WHERE id=%s"

    with conn.cursor() as cursor:
        cursor.execute(query, values)
        conn.commit()

    return {
        "message": "Clarity call updated successfully",
        "call_id": call_id,
        "updated_fields": update_data
    }



# GET → All Clarity Calls (Admin)
@students_router_admin.get("/")
def get_all_clarity_calls(
    admin=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    
    query = """
        SELECT id, student_id, mentor_name, call_status, scheduled_date, notes
        FROM clarity_calls
        ORDER BY scheduled_date DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if not rows:
        return {"message": "No clarity call records found", "data": []}

    return {"data": rows}





# DELETE → Delete Clarity Call
@students_router_admin.delete("/delete/{call_id}")
def delete_clarity_call(
    call_id: int,
    admin=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM clarity_calls WHERE id=%s", (call_id,))
        affected = cursor.rowcount
        conn.commit()

    if affected == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Clarity Call {call_id} not found"
        )

    return {"message": f"Clarity Call {call_id} deleted successfully"}
