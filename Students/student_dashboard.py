from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student

student_dashboard_router = APIRouter(prefix="/student/dashboard", tags=["Student Dashboard"])

@student_dashboard_router.get("/profile")
def get_student_dashboard(student=Depends(require_student), conn=Depends(get_db_connection)):
    
    if not student:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    student_id = student["student_id"]

    query = """
        SELECT 
            s.student_id, s.first_name, s.last_name, s.email, s.phone, s.address,
            s.profession, s.designation, s.gender,
            se.status AS enrollment_status, se.enrollment_date,
            b.batch_name, b.status AS batch_status,
            w.name AS workshop_name
        FROM students s
        LEFT JOIN student_enrollments se ON s.student_id = se.student_id
        LEFT JOIN batches b ON se.batch_id = b.id
        LEFT JOIN workshops w ON se.workshop_id = w.workshop_id
        WHERE s.student_id = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="Student not found")

    # Build base student info
    student_info = {
        "student_id": rows[0]["student_id"],
        "first_name": rows[0]["first_name"],
        "last_name": rows[0]["last_name"],
        "email": rows[0]["email"],
        "phone": rows[0]["phone"],
        "address": rows[0]["address"],
        "profession": rows[0]["profession"],
        "designation": rows[0]["designation"],
        "gender": rows[0]["gender"],
        "enrollments": []
    }

    # Add enrollment info if available
    for row in rows:
        if row["workshop_name"] and row["batch_name"]:
            student_info["enrollments"].append({
                "status": row["enrollment_status"],
                "enrollment_date": str(row["enrollment_date"].date()) if row["enrollment_date"] else None,
                "batch": {
                    "batch_name": row["batch_name"],
                    "status": row["batch_status"]
                },
                "workshop": {
                    "workshop_name": row["workshop_name"]
                }
            })

    full_response = {
        "message": f"Welcome {student_info['first_name']} {student_info['last_name']}!",
        "student": student_info
    }

    return full_response





# # -----------------------------
# #  CLARITY CALL STATUS
# # -----------------------------
# @student_dashboard_router.get("/clarity_call_status")
# def get_clarity_call_status(student=Depends(require_student), conn=Depends(get_db_connection)):
#     if not student:
#         raise HTTPException(status_code=401, detail="Unauthorized access")

#     student_id = student["student_id"]

#     query = """
#         SELECT call_status, scheduled_date, mentor_name
#         FROM clarity_calls
#         WHERE student_id = %s
#         ORDER BY scheduled_date DESC
#         LIMIT 1
#     """

#     with conn.cursor(dictionary=True) as cursor:
#         cursor.execute(query, (student_id,))
#         record = cursor.fetchone()

#     if not record:
#         return {"clarity_call_status": "Not Scheduled"}

#     return {
#         "clarity_call_status": record["call_status"],
#         "scheduled_date": str(record["scheduled_date"]) if record["scheduled_date"] else None,
#         "mentor_name": record["mentor_name"]
#     }


# # -----------------------------
# #  PROFILE COMPLETION
# # -----------------------------
# @student_dashboard_router.get("/profile_completion")
# def get_profile_completion(student=Depends(require_student), conn=Depends(get_db_connection)):
#     if not student:
#         raise HTTPException(status_code=401, detail="Unauthorized access")

#     student_id = student["student_id"]

#     query = """
#         SELECT first_name, last_name, email, phone, address, profession, designation, gender
#         FROM students WHERE student_id = %s
#     """

#     with conn.cursor(dictionary=True) as cursor:
#         cursor.execute(query, (student_id,))
#         data = cursor.fetchone()

#     if not data:
#         raise HTTPException(status_code=404, detail="Student not found")

#     required_fields = ["first_name", "last_name", "email", "phone", "address", "profession", "designation", "gender"]
#     filled_fields = [f for f in required_fields if data.get(f)]
#     missing_fields = [f for f in required_fields if not data.get(f)]

#     completion_percent = round((len(filled_fields) / len(required_fields)) * 100, 2)

#     return {
#         "profile_completion": f"{completion_percent}%",
#         "filled_fields": filled_fields,
#         "missing_fields": missing_fields
#     }


# # -----------------------------
# #  CLEANUP TEMP DATA
# # -----------------------------
# @student_dashboard_router.delete("/cleanup_inprogress_data")
# def cleanup_inprogress_data(student=Depends(require_student), conn=Depends(get_db_connection)):
#     if not student:
#         raise HTTPException(status_code=401, detail="Unauthorized access")

#     student_id = student["student_id"]

#     with conn.cursor() as cursor:
#         # Remove in-progress assignments
#         cursor.execute("""
#             DELETE FROM student_assignments 
#             WHERE student_id = %s AND status IN ('In Progress', 'Draft')
#         """, (student_id,))

#         # Remove old in-progress progress data
#         cursor.execute("""
#             DELETE FROM student_progress 
#             WHERE student_id = %s AND progress_status = 'In Progress'
#         """, (student_id,))

#     conn.commit()
#     return {"message": "Removed all in-progress and assignment data successfully."}
