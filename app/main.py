import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from app.routers import health, predict, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリ起動時に Redis 接続を作成し、
    終了時に接続を閉じる
    """
    app.state.redis = Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True
    )
    yield
    app.state.redis.close()


app = FastAPI(
    title="CNN Defect Detection API",
    lifespan=lifespan
)

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
