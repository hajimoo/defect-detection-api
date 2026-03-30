import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, predict

app = FastAPI(title="CNN Defect Detection API")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:80").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
