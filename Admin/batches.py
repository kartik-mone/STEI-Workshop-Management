from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_admin

batches_router = APIRouter(prefix="/batches", tags=["Batches"])


# Pydantic model for adding/updating batches
class BatchUpdate(BaseModel):
    workshop_id: Optional[int] = None
    batch_name: Optional[str] = None
    instructor: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    zoom_link: Optional[str] = None
    zoom_meeting_id: Optional[str] = None
    zoom_password: Optional[str] = None


# ADMIN ROUTES

# Add Batch (Admin only)
@batches_router.post("/add")
async def add_batch(
    batch: BatchUpdate,
    conn=Depends(get_db_connection),
    user=Depends(require_admin)
):
    if not batch.workshop_id:
        raise HTTPException(status_code=400, detail="No workshop_id provided")

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT name, category_id FROM workshops WHERE workshop_id=%s",
            (batch.workshop_id,)
        )
        workshop = cursor.fetchone()
        if not workshop:
            raise HTTPException(status_code=404, detail="Invalid workshop_id")

        try:
            query = """INSERT INTO batches 
                (workshop_id, category_id, workshop_name, batch_name, instructor, 
                start_date, start_time, end_time, location, status, zoom_link, 
                zoom_meeting_id, zoom_password)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(query, (
                batch.workshop_id, workshop["category_id"], workshop["name"],
                batch.batch_name, batch.instructor, batch.start_date, batch.start_time,
                batch.end_time, batch.location, batch.status, batch.zoom_link,
                batch.zoom_meeting_id, batch.zoom_password
            ))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Batch added successfully by Admin {user['admin_id']}"}


# Update Batch (Admin only)
@batches_router.put("/update/{batch_id}")
async def update_batch(
    batch_id: int,
    batch: BatchUpdate,
    conn=Depends(get_db_connection),
    user=Depends(require_admin)
):
    data = batch.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    allowed_fields = [
        "batch_name", "instructor", "status", "start_date", "start_time",
        "end_time", "location", "zoom_link", "zoom_meeting_id", "zoom_password"
    ]

    fields = []
    values = []

    for key in allowed_fields:
        if key in data:
            fields.append(f"{key}=%s")
            values.append(data[key])

    query = f"UPDATE batches SET {', '.join(fields)} WHERE id=%s"
    values.append(batch_id)

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(values))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Batch updated successfully by Admin {user['admin_id']}"}


# Delete Batch (Admin only)
@batches_router.delete("/delete/{batch_id}")
async def delete_batch(
    batch_id: int,
    conn=Depends(get_db_connection),
    user=Depends(require_admin)
):
    with conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM batches WHERE id=%s", (batch_id,))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Batch deleted successfully by Admin {user['admin_id']}"}


# PUBLIC ROUTES

# Get all batches (Public)
@batches_router.get("/")
async def get_batches(conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM batches")
        rows = cursor.fetchall()

    for row in rows:
        for key in ["start_time", "end_time", "created_at", "updated_at"]:
            if key in row and row[key] is not None:
                row[key] = str(row[key])

    return rows if rows else {"message": "No batches found"}


# Get batch by ID (Public)
@batches_router.get("/{batch_id}")
async def get_batch(batch_id: int, conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM batches WHERE id=%s", (batch_id,))
        batch = cursor.fetchone()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    for key in ["start_time", "end_time", "created_at", "updated_at"]:
        if key in batch and batch[key] is not None:
            batch[key] = str(batch[key])

    return batch
