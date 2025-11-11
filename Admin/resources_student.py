from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_admin

resource_router = APIRouter(prefix="/auth/resources", tags=["Resources"])

# POST → Add Resource
#  -----------------------------------------
@resource_router.post("/create")
def add_resource(
    data: dict,
    user=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    required = ["name", "category_id", "url"]
    for field in required:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    name = data["name"]
    category_id = data["category_id"]
    session_id = data.get("session_id")
    url = data["url"]
    description = data.get("description")

        
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO resources (name, category_id, session_id,  url, description)
            VALUES (%s,  %s, %s, %s, %s, %s)
            """,
            (name, category_id, session_id, url, description)
        )
        conn.commit()

    return {
        "message": "Resource added successfully"
    }


'''
Example JSON body for adding a resource:

{
  "name": "NumPy Cheatsheet",
  "category_id": 1,
  "session_id": 10,
  "url": "https://example.com/numpy.pdf",
  "description": "Summary of NumPy essentials"
}
'''

# PUT → Update Resource
# -----------------------------------------
@resource_router.put("/update/{resource_id}")
def update_resource(
    resource_id: int,
    data: dict,
    user=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    allowed_fields = ["name", "category_id", "session_id", "url", "description"]

    # Filter valid fields only
    update_fields = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided")

    set_clause = ", ".join([f"{k}=%s" for k in update_fields.keys()])
    values = list(update_fields.values())
    values.append(resource_id)

    query = f"UPDATE resources SET {set_clause} WHERE id=%s"

    with conn.cursor() as cursor:
        cursor.execute(query, tuple(values))
        affected = cursor.rowcount
        conn.commit()

    if affected == 0:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")

    return {
        "message": f"Resource {resource_id} updated successfully"
    }


# GET → Fetch Resources
#  -----------------------------------------
@resource_router.get("/all_resources")
def get_resources(
    user=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    query = """
        SELECT r.id, r.name, r.session_name, r.url, r.description, rc.name AS category
        FROM resources r
        JOIN resource_categories rc ON r.category_id = rc.id
        ORDER BY r.created_at DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        resources = cursor.fetchall()

    if not resources:   
        return {"message": "No resources available", "resources": []}

    return {"resources": resources}


# DELETE → Delete Resource
#  -----------------------------------------
@resource_router.delete("/delete/{resource_id}")
def delete_resource(
    resource_id: int,
    user=Depends(require_admin),
    conn=Depends(get_db_connection)
):
    
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM resources WHERE id=%s", (resource_id,))
        affected = cursor.rowcount
        conn.commit()

    if affected == 0:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")

    return {"message": f"Resource {resource_id} deleted successfully"}
