from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database.db import get_db_connection
from auth.jwt.jwt_auth import require_admin   

quotes_router = APIRouter(prefix="/quotes", tags=["Quotes"])

# Radio value → hex code
COLOR_MAP = {
    "Yellow": "#FFFF00",
    "Blue": "#0000FF",
    "Green": "#008000",
    "Red": "#FF0000",
    "Purple": "#800080"
}


# Pydantic model for adding/updating quotes
class QuoteBase(BaseModel):
    quote: str
    author: Optional[str] = None
    category: str
    color: Optional[str] = None
    featured: Optional[bool] = False


class QuoteUpdate(BaseModel):
    quote: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    featured: Optional[bool] = None


# Add new quote (Admin only)
@quotes_router.post("/add")
async def add_quote(data: QuoteBase,
                    conn=Depends(get_db_connection),
                    user=Depends(require_admin)):
    color_hex = COLOR_MAP.get(data.color) if data.color else None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO quotes (quote, author, category, color, featured)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (data.quote, data.author, data.category, color_hex, data.featured)
            )
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Quote added successfully by Admin {user['admin_id']}"}


# Get all quotes (Public)
@quotes_router.get("/")
async def get_quotes(conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, quote, author, category, color, featured, created_at, updated_at
            FROM quotes
            ORDER BY created_at DESC
            """
        )
        quotes = cursor.fetchall()

    return quotes if quotes else {"message": "No quotes found"}


# Get specific quote (Public)
@quotes_router.get("/{quote_id}")
async def get_quote(quote_id: int, conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, quote, author, category, color, featured, created_at, updated_at
            FROM quotes
            WHERE id = %s
            """,
            (quote_id,)
        )
        quote = cursor.fetchone()

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    return quote


# Update quote dynamically (Admin only)
@quotes_router.put("/update/{quote_id}")
async def update_quote(quote_id: int,
                       data: QuoteUpdate,
                       conn=Depends(get_db_connection),
                       user=Depends(require_admin)):
    update_data = data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    fields = []
    values = []

    for key, value in update_data.items():
        if key == "color":
            fields.append("color=%s")
            values.append(COLOR_MAP.get(value) if value else None)
        else:
            fields.append(f"{key}=%s")
            values.append(value)

    values.append(quote_id)
    query = f"UPDATE quotes SET {', '.join(fields)}, updated_at=NOW() WHERE id=%s"

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(values))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Quote not found")
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Quote {quote_id} updated successfully by Admin {user['admin_id']}"}


# Delete quote (Admin only)
@quotes_router.delete("/delete/{quote_id}")
async def delete_quote(quote_id: int,
                       conn=Depends(get_db_connection),
                       user=Depends(require_admin)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM quotes WHERE id=%s", (quote_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Quote not found")
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Quote {quote_id} deleted successfully by Admin {user['admin_id']}"}
