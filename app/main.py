from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, predict

app = FastAPI(title="CNN Defect Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
