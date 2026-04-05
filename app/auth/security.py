from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


# JWT署名に使う秘密鍵
# 実務ではコードに直接書かず、環境変数で管理するのが望ましい
SECRET_KEY = "your-secret-key-change-this"

# JWT署名アルゴリズム
ALGORITHM = "HS256"


# bcrypt を使ってパスワードをハッシュ化するための設定
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Swagger UI の Authorize ボタンや Depends(get_current_user) で使う設定
# tokenUrl はログインAPIのURLに合わせる
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


def hash_password(password: str) -> str:
    """
    パスワードをハッシュ化する関数

    平文のままDBに保存すると危険なので、
    必ずハッシュ化して保存する。
    """
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    入力された平文パスワードと
    DBに保存されたハッシュ済みパスワードを比較する関数
    """
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    """
    JWTアクセストークンを生成する関数

    payload には以下の情報を入れる:
    - sub: username
    - id: user_id
    - exp: 有効期限
    """
    encode = {
        "sub": username,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + expires_delta
    }

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    リクエストの Authorization: Bearer <token> を読み取り、
    JWT を検証して現在のユーザー情報を返す関数

    トークンが無効な場合は 401 Unauthorized を返す。
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        user_id = payload.get("id")

        # payload に必要な情報がない場合は認証失敗とみなす
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        return {
            "username": username,
            "id": user_id
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )
