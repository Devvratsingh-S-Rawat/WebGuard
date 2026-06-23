from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import scan
import os

app = FastAPI(
    title="WebGuard API",
    description="Website Vulnerability Scanner Backend",
    version="1.0.0"
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "WebGuard API is running 🛡️"}