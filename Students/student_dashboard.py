from fastapi import APIRouter, Depends, HTTPException
from auth import require_student  

student_dashboard_router = APIRouter(
    prefix="/student-dashboard",
    tags=["Student Dashboard"]
)


# Student Dashboard - Student only
@student_dashboard_router.get("/")
def student_dashboard(user=Depends(require_student)):
    """
    Returns a welcome message for the logged-in student.
    `require_student` validates the JWT and fetches student details.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    return {
        "message": f"Welcome {full_name} to your dashboard",
        "student_id": user["student_id"]
    }
