from fastapi import FastAPI
from app.routers import health, predict

app = FastAPI(title="CNN Defect Detection API")

app.include_router(health.router)
app.include_router(predict.router)
