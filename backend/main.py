from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import urls
from routers import analytics

models.Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="URL Shortener",
    description="A distributed URL shortener with Redis caching",
    version="1.0.0"
)
     
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status":"ok"}

app.include_router(urls.router)
app.include_router(analytics.router)