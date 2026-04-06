from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

from app.db.database import get_connection


# =========================
# JWT設定
# =========================

# JWT署名に使う秘密鍵
# 実務ではコードに直接書かず、環境変数で管理する
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY 環境変数が設定されていません。")

# JWT署名アルゴリズム
ALGORITHM = "HS256"


# =========================
# パスワードハッシュ設定
# =========================

# bcrypt を使ってパスワードをハッシュ化する設定
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# OAuth2設定
# =========================

# Swagger UI の Authorize ボタンや Depends(get_current_user) で使用する
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


# =========================
# パスワード関連関数
# =========================

def hash_password(password: str) -> str:
    """
    パスワードをハッシュ化する関数

    平文のままDBに保存すると危険なため、
    必ずハッシュ化して保存する。
    """
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    入力された平文パスワードと
    DBに保存されたハッシュ済みパスワードを比較する関数
    """
    return bcrypt_context.verify(plain_password, hashed_password)


# =========================
# JWT生成関数
# =========================

def create_access_token(
    username: str,
    user_id: int,
    token_version: int,
    expires_delta: timedelta
) -> str:
    """
    JWTアクセストークンを生成する関数

    payload には以下の情報を含める:
    - sub: username
    - id: user_id
    - token_version: トークンのバージョン
    - exp: 有効期限
    """
    encode = {
        "sub": username,
        "id": user_id,
        "token_version": token_version,
        "exp": datetime.now(timezone.utc) + expires_delta
    }

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# 現在ユーザー取得関数
# =========================

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Authorization: Bearer <token> を読み取り、
    JWTを検証したうえで現在のユーザー情報を返す関数

    処理の流れ:
    1. JWTをデコードする
    2. payload から user 情報を取得する
    3. DBから現在のユーザー状態を再確認する
    4. 退会済みかどうかを確認する
    5. token_version が一致するか確認する
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user."
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        user_id = payload.get("id")
        token_version = payload.get("token_version")

        # payload に必要な値がない場合は認証失敗
        if username is None or user_id is None or token_version is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # DBから現在のユーザー状態を確認する
        cursor.execute(
            """
            SELECT id, username, is_deleted, token_version
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        user = cursor.fetchone()

        # ユーザーが存在しない場合
        if not user:
            raise credentials_exception

        # 退会済みユーザーは認証不可
        if user["is_deleted"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deleted."
            )

        # token_version が一致しない場合、
        # 古いトークンとみなして認証を拒否する
        if user["token_version"] != token_version:
            raise credentials_exception

        return {
            "id": user["id"],
            "username": user["username"],
            "token_version": user["token_version"]
        }

    finally:
        cursor.close()
        conn.close()
