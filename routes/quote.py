from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from db import get_db_connection

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
class QuoteUpdate(BaseModel):
    quote: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None


# Add new quote
@quotes_router.post("/add")
async def add_quote(quote: QuoteUpdate, conn=Depends(get_db_connection)):
    if not quote.quote or not quote.category:
        raise HTTPException(status_code=400, detail="quote and category are required")

    color_hex = COLOR_MAP.get(quote.color)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO quotes (quote, author, category, color, featured)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (quote.quote, quote.author, quote.category, color_hex, quote.featured)
        )
        conn.commit()

    return {"message": "Quote added successfully"}


# Get all quotes
@quotes_router.get("/")
async def get_quotes(conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, quote, author, category, color, featured, created_at, updated_at
            FROM quotes
            """
        )
        quotes = cursor.fetchall()

    return quotes if quotes else {"message": "No quotes found"}


# Get specific quote
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


# Update quote dynamically
@quotes_router.put("/{quote_id}")
async def update_quote(quote_id: int, data: QuoteUpdate, conn=Depends(get_db_connection)):
    update_data = data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    fields = []
    values = []

    for key, value in update_data.items():
        if key == "color":
            fields.append("color=%s")
            values.append(COLOR_MAP.get(value))
        else:
            fields.append(f"{key}=%s")
            values.append(value)

    values.append(quote_id)
    query = f"UPDATE quotes SET {', '.join(fields)} WHERE id=%s"

    with conn.cursor() as cursor:
        cursor.execute(query, tuple(values))
        conn.commit()

    return {"message": "Quote updated successfully"}


# Delete quote
@quotes_router.delete("/{quote_id}")
async def delete_quote(quote_id: int, conn=Depends(get_db_connection)):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM quotes WHERE id=%s", (quote_id,))
        conn.commit()

    return {"message": "Quote deleted successfully"}
