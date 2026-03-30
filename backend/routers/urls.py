from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import URL
from schemas import URLCreate, URLResponse
from shortener import encode
from cache import get_cached_url, set_cached_url, increment_clicks, is_rate_limited
import os

router=APIRouter()

BASE_URL = os.getenv("BASE_URL","http://localhost:8000")

@router.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, request:Request, db: Session = Depends(get_db)):
    client_ip=request.client.host

    if is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute."
        )
    original_url=str(payload.original_url)
    existing=db.query(URL).filter(URL.original_url==original_url).first()
    if existing:
        return{
            **existing.__dict__,
            "short_url":f"{BASE_URL}/{existing.short_code}"
        }
    db_url=URL(original_url=original_url, short_code="temp")
    db.add(db_url)
    db.flush()

    short_code=encode(db_url.id)
    db_url.short_code=short_code
    db.commit()
    db.refresh(db_url)

    set_cached_url(short_code,original_url)

    return{
        **db_url.__dict__,
        "short_url":f"{BASE_URL}/{short_code}"
    }

@router.get("/{short_code}")
def redirect_url(short_code:str, db:Session=Depends(get_db)):
    original_url=get_cached_url(short_code)

    if not original_url:
        db_url=db.query(URL).filter(URL.short_code==short_code).first()
        if not db_url:
            raise HTTPException(status_code=404, detail="Short URL not found")
        original_url=db_url.original_url
        set_cached_url(short_code,original_url)

    increment_clicks(short_code)

    return RedirectResponse(url=original_url)