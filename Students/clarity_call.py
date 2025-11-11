from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student
from pydantic import BaseModel
from typing import List

clarity_call_router = APIRouter(
    prefix="/student/clarity_call",
    tags=["Clarity Call"]
)

# 1) GET → Clarity Call Status
# ------------------------------

@clarity_call_router.get("/clarity_call_status")
def get_clarity_call_status(student=Depends(require_student), conn=Depends(get_db_connection)):

    student_id = student["student_id"]

    query = """
        SELECT call_status
        FROM clarity_calls
        WHERE student_id = %s
        ORDER BY scheduled_date DESC
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (student_id,))
        record = cursor.fetchone()

    if not record:
        return {"clarity_call_status": "Not Scheduled"}

    return {"clarity_call_status": record["call_status"]}


# 2) GET → Call History
# ----------------------

@clarity_call_router.get("/history")
def clarity_call_history(student=Depends(require_student), conn=Depends(get_db_connection)):

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


# 3) GET → Fetch Questions Only
# -----------------------------

@clarity_call_router.get("/precall_questionnaire")
def get_pre_call_questions(student=Depends(require_student), conn=Depends(get_db_connection)):

    query = """
        SELECT id, question, options
        FROM clarity_questions
        ORDER BY id ASC
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No questions found")

    return {"questions": rows}




class AnswerItem(BaseModel):
    question_id: int
    answer: str   # must be A / B / C / D


class SubmitPayload(BaseModel):
    responses: List[AnswerItem]


# 4) POST → Submit Pre-Call Questionnaire Responses
# -------------------------------------------------

@clarity_call_router.post("/submit_precall_questionnaire")
def submit_pre_call_responses(
    payload: SubmitPayload,
    student=Depends(require_student),
    conn=Depends(get_db_connection)
):

    student_id = student["student_id"]

    if not payload.responses:
        raise HTTPException(status_code=400, detail="No responses submitted")

    # validation
    for r in payload.responses:
        if r.answer not in ["A", "B", "C", "D"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer '{r.answer}' for question {r.question_id}"
            )

    with conn.cursor() as cursor:
        for r in payload.responses:
            cursor.execute(
                """
                INSERT INTO clarity_responses (student_id, question_id, answer)
                VALUES (%s, %s, %s)
                """,
                (student_id, r.question_id, r.answer),
            )
        conn.commit()

    return {"message": "Responses saved successfully"}


# 5) GET → See Submitted Responses
# --------------------------------

@clarity_call_router.get("/precall_questionnaire_responses")
def get_student_responses(
    student=Depends(require_student),
    conn=Depends(get_db_connection)
):

    student_id = student["student_id"]

    query = """
        SELECT q.question, r.answer
        FROM clarity_responses r
        JOIN clarity_questions q ON r.question_id = q.id
        WHERE r.student_id = %s
        ORDER BY r.question_id ASC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()

    return {"responses": rows or []}
