from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import URL
from cache import get_cached_clicks

router=APIRouter()

@router.get("/stats/{short_code}")
def get_stats(short_code:str, db:Session=Depends(get_db)):
    db_url=db.query(URL).filter(URL.short_code==short_code).first()

    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    clicks=get_cached_clicks(short_code)

    return{
        "short_code":short_code,
        "original_url":db_url.original_url,
        "short_url":f"http://localhost:8000/{short_code}",
        "clicks":clicks,
        "created_at":db_url.created_at
    }
