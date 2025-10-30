from fastapi import APIRouter, Depends, HTTPException
from auth.jwt.jwt_auth import require_admin
from database.db import get_db_connection

admin_dashboard_router = APIRouter(
    prefix="/admin-dashboard",
    tags=["Admin Dashboard"]
)


@admin_dashboard_router.get("/")
def admin_dashboard(user=Depends(require_admin), conn=Depends(get_db_connection)):
    """
    Admin Dashboard API.
    Returns total revenue, workshops, active batches,
    recent workshops, and upcoming batches.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    dashboard_data = {}

    with conn.cursor() as cursor:

        # Total Revenue (fix here)
        cursor.execute("""
            SELECT COALESCE(SUM(w.fee), 0) AS total_revenue
            FROM student_enrollments se
            JOIN workshops w ON se.workshop_id = w.workshop_id
        """)
        revenue = cursor.fetchone()
        dashboard_data["total_revenue"] = revenue["total_revenue"]


        # Total Workshops
        cursor.execute("SELECT COUNT(*) AS total_workshops FROM workshops")
        workshops_count = cursor.fetchone()
        dashboard_data["total_workshops"] = workshops_count["total_workshops"]


        # Active Batches
        cursor.execute("SELECT COUNT(*) AS active_batches FROM batches WHERE status='Ongoing'")
        batches_count = cursor.fetchone()
        dashboard_data["active_batches"] = batches_count["active_batches"]


        # Recent Workshops (latest 5)
        cursor.execute("""
            SELECT name, category_name, duration_days, start_date, status
            FROM workshops
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_workshops = cursor.fetchall()
        
        dashboard_data["recent_workshops"] = [
            {
                "Workshop Name": w["name"],
                "Category": w["category_name"],
                "Duration": w["duration_days"],
                "Start Date": str(w["start_date"]) if w["start_date"] else "-",
                "Status": w["status"]
            }
            for w in recent_workshops
        ]

        # Upcoming Batches (future start_date)
        cursor.execute("""
            SELECT b.batch_name, b.start_date, b.status,
                   w.name AS workshop_name,
                   (SELECT COUNT(*) FROM student_enrollments se WHERE se.batch_id = b.id) AS students
            FROM batches b
            JOIN workshops w ON b.workshop_id = w.workshop_id
            WHERE b.start_date >= CURRENT_DATE
            ORDER BY b.start_date ASC
            LIMIT 5
        """)
        upcoming_batches = cursor.fetchall()
        dashboard_data["upcoming_batches"] = [
            {
                # "batch_id": b["batch_id"],
                "Batch Name": b["batch_name"],
                "Workshop": b["workshop_name"],
                "Start Date": str(b["start_date"]),
                "Students": b["students"],
                "Status": b["status"]
            }
            for b in upcoming_batches
        ]

    return {
        "message": f"Welcome Admin {user['first_name']}",
        "admin_id": user["admin_id"],
        "dashboard": dashboard_data
    }
