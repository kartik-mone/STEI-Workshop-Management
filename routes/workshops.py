from fastapi import APIRouter, HTTPException, Request, Depends
from db import get_db_connection

workshops_router = APIRouter(prefix="/workshops", tags=["Workshops"])


# Add Workshop
@workshops_router.post("/add")
async def add_workshop(request: Request, conn=Depends(get_db_connection)):
    data = await request.json()

    if not data:
        raise HTTPException(status_code=400, detail="No data provided")

    cursor = conn.cursor()

    # 1. Fetch category_name from categories table
    cursor.execute("SELECT name FROM categories WHERE category_id = %s", (data["category_id"],))
    category = cursor.fetchone()
    if not category:
        cursor.close()
        raise HTTPException(status_code=400, detail="Invalid category_id")

    category_name = category["name"]

    # 2. Insert workshop with category_id and category_name
    query = """INSERT INTO workshops (
                category_id, category_name, name, description, duration_days, 
                minutes_per_session, sessions_per_day, capacity, fee, instructor, 
                status, workshop_image, start_date
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    
    cursor.execute(query, (
        data["category_id"], category_name, data["name"], data.get("description"),
        data["duration_days"], data.get("minutes_per_session", 60),
        data.get("sessions_per_day", 1), data.get("capacity", 0),
        data.get("fee", 0), data.get("instructor"),
        data.get("status", "Upcoming"), data.get("workshop_image"),
        data.get("start_date")
    ))
    conn.commit()
    cursor.close()

    return {"message": "Workshop added successfully"}


# Get all workshops
@workshops_router.get("/")
async def get_workshops(conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workshops")
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return {"message": "No workshops found"}
    return result


# Get specific workshop
@workshops_router.get("/{workshop_id}")
async def get_workshop(workshop_id: int, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workshops WHERE workshop_id = %s", (workshop_id,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        raise HTTPException(status_code=404, detail="Workshop not found")
    return result


# Update workshop
@workshops_router.put("/{workshop_id}")
async def update_workshop(workshop_id: int, request: Request, conn=Depends(get_db_connection)):
    data = await request.json()

    if not data:
        raise HTTPException(status_code=400, detail="No data provided")

    cursor = conn.cursor()
    fields = []
    values = []

    # Only allow updating certain fields
    for key in ["name", "description", "duration_days", "minutes_per_session",
                "sessions_per_day", "capacity", "fee", "instructor", "status", "workshop_image", "start_date"]:
        if key in data:
            fields.append(f"{key}=%s")
            values.append(data[key])

    if not fields:
        cursor.close()
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    query = f"UPDATE workshops SET {', '.join(fields)} WHERE workshop_id=%s"
    values.append(workshop_id)

    cursor.execute(query, tuple(values))
    conn.commit()
    cursor.close()

    return {"message": "Workshop updated successfully"}


# Delete workshop
@workshops_router.delete("/{workshop_id}")
async def delete_workshop(workshop_id: int, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workshops WHERE workshop_id = %s", (workshop_id,))
    conn.commit()
    cursor.close()

    return {"message": "Workshop deleted successfully"}
