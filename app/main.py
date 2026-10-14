from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from routers.auth import router as auth_router
from routers.reports import router as reports_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CivicFix API")

@app.get("/")
def root():
    return {
        "name": "CivicFix API",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://civicfix-frontend-ekqm.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(reports_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API is running"}


@app.get("/api/db-check")
def database_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database": "connected"}