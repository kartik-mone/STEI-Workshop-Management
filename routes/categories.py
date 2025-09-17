from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db_connection

router = APIRouter(prefix="/categories", tags=["Categories"])

# Pydantic model for validation
class Category(BaseModel):
    name: str


# Add Category
@router.post("/add")
def add_category(category: Category, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category.name,))
        conn.commit()
        return {"message": "Category added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()


# Get All Categories
@router.get("/")
def get_categories(conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    result = cursor.fetchall()
    cursor.close()

    if not result:
        return {"message": "No categories found"}
    return result


# Get Specific Category
@router.get("/{category_id}")
def get_category(category_id: int, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return result


# Update Category
@router.put("/{category_id}")
def update_category(category_id: int, category: Category, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("UPDATE categories SET name=%s WHERE category_id=%s", (category.name, category_id))
    conn.commit()
    cursor.close()
    return {"message": "Category updated successfully"}


# Delete Category
@router.delete("/{category_id}")
def delete_category(category_id: int, conn=Depends(get_db_connection)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
    conn.commit()
    cursor.close()
    return {"message": "Category deleted successfully"}
