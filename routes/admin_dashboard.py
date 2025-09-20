from fastapi import APIRouter, Depends, HTTPException
from auth import require_admin  # Ensures only logged-in admins can access
from db import get_db_connection

admin_dashboard_router = APIRouter(
    prefix="/admin-dashboard",
    tags=["Admin Dashboard"]
)


# Admin Dashboard - Admin only
@admin_dashboard_router.get("/")
def admin_dashboard(user=Depends(require_admin), conn=Depends(get_db_connection)):
    """
    Returns a welcome message for the logged-in admin.
    `require_admin` validates the JWT and fetches admin details.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    
    return {
        "message": f"Welcome Admin {user['first_name']}",
        "admin_id": user["admin_id"]
    }
