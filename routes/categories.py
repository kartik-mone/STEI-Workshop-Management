from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db_connection
from auth import require_admin   # Only admins can modify categories

router = APIRouter(prefix="/categories", tags=["Categories"])


class Category(BaseModel):
    name: str


# ADMIN ROUTES

# Add Category (Admin only)
@router.post("/add")
def add_category(category: Category,
                 conn=Depends(get_db_connection),
                 user=Depends(require_admin)):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category.name,))
        conn.commit()
        return {"message": f"Category added successfully by Admin {user['admin_id']}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()


# Update Category (Admin only)
@router.put("/update/{category_id}")
def update_category(category_id: int,
                    category: Category,
                    conn=Depends(get_db_connection),
                    user=Depends(require_admin)):
    cursor = conn.cursor()
    cursor.execute("UPDATE categories SET name=%s WHERE category_id=%s", (category.name, category_id))
    conn.commit()
    cursor.close()
    return {"message": f"Category updated successfully by Admin {user['admin_id']}"}


# Delete Category (Admin only)
@router.delete("/delete/{category_id}")
def delete_category(category_id: int,
                    conn=Depends(get_db_connection),
                    user=Depends(require_admin)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
    conn.commit()
    cursor.close()
    return {"message": f"Category deleted successfully by Admin {user['admin_id']}"}


# PUBLIC ROUTES

# Get All Categories (Public)
@router.get("/")
def get_categories(conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return {"message": "No categories found"}
    return result


# Get Specific Category (Public)
@router.get("/{category_id}")
def get_category(category_id: int,
                 conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return result
