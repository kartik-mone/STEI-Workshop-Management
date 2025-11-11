from fastapi import APIRouter, Depends, HTTPException
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_student

resource_router = APIRouter(prefix="/auth/resources", tags=["Resources"])


# GET → Fetch Resources
#  -----------------------------------------
@resource_router.get("/")
def get_resources(
    student=Depends(require_student),
    conn=Depends(get_db_connection)
):
    student_id = student["student_id"]

    # Verify profile completion
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT profile_completed FROM students WHERE student_id=%s",
            (student_id,)
        )
        result = cursor.fetchone()

    if not result or not result["profile_completed"]:
        raise HTTPException(
            status_code=403,
            detail="Profile must be 100% completed to access resources"
        )

    query = """
        SELECT r.id, r.name, r.url, r.description, rc.name AS category
        FROM resources r
        JOIN resource_categories rc ON r.category_id = rc.id
        ORDER BY r.created_at DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        resources = cursor.fetchall()

    return {"resources": resources}


# GET → Fetch Resource Categories
#  -----------------------------------------
@resource_router.get("/categories")
def get_resource_categories(student=Depends(require_student), conn=Depends(get_db_connection)):
    query = "SELECT name FROM resource_categories ORDER BY name"

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return {"categories": rows}
