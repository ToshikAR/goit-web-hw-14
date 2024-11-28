import logging
from fastapi import Depends, HTTPException
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(prefix="/index", tags=["index"])


@router.get("/")
def index():
    return {"message": "Contact Application"}


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as err:
        logging.error(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")
