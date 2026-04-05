import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, predict, auth

app = FastAPI(title="CNN Defect Detection API")

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:80"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証ルーターを登録する
app.include_router(auth.router)

# ヘルスチェック用ルーターを登録する
app.include_router(health.router)

# 画像推論APIルーターを登録する
app.include_router(predict.router)
