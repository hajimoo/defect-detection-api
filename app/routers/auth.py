from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.db.database import get_connection
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.schemas import (
    CreateUserRequest,
    TokenResponse,
    ChangePasswordRequest,
    DeleteUserRequest,
    RefreshTokenRequest,
    LogoutRequest,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def delete_all_user_refresh_tokens(redis_client, user_id: int):
    """
    指定ユーザーの全 refresh token を Redis から削除する関数
    """
    session_key = f"user_refresh_tokens:{user_id}"
    token_keys = redis_client.smembers(session_key)

    for token_key in token_keys:
        redis_client.delete(token_key)

    redis_client.delete(session_key)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: CreateUserRequest):
    """
    ユーザー登録API

    処理の流れ:
    1. username の重複チェック
    2. パスワードをハッシュ化
    3. users テーブルに保存
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (request.username,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists."
            )

        hashed_password = hash_password(request.password)

        cursor.execute(
            """
            INSERT INTO users (username, hashed_password)
            VALUES (%s, %s)
            """,
            (request.username, hashed_password)
        )
        conn.commit()

        return {
            "message": "User created successfully.",
            "username": request.username
        }

    finally:
        cursor.close()
        conn.close()


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    ログインAPI

    処理の流れ:
    1. username でユーザー検索
    2. 退会済みユーザーか確認
    3. パスワード照合
    4. access token / refresh token を発行
    5. refresh token を Redis に保存
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, username, hashed_password, is_deleted, token_version
            FROM users
            WHERE username = %s
            """,
            (form_data.username,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        if user["is_deleted"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deleted."
            )

        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        access_token = create_access_token(
            username=user["username"],
            user_id=user["id"],
            token_version=user["token_version"],
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = create_refresh_token(
            username=user["username"],
            user_id=user["id"],
            token_version=user["token_version"],
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        redis_client = request.app.state.redis
        refresh_payload = decode_token(refresh_token)
        jti = refresh_payload["jti"]

        redis_key = f"refresh:{user['id']}:{jti}"
        session_set_key = f"user_refresh_tokens:{user['id']}"

        redis_client.setex(
            redis_key,
            60 * 60 * 24 * REFRESH_TOKEN_EXPIRE_DAYS,
            refresh_token
        )
        redis_client.sadd(session_set_key, redis_key)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    finally:
        cursor.close()
        conn.close()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    body: RefreshTokenRequest
):
    """
    アクセストークン再発行API

    処理の流れ:
    1. refresh token を検証
    2. Redis に保存された token と一致するか確認
    3. DB の token_version を確認
    4. 新しい access token / refresh token を再発行
    5. 古い refresh token は削除する
    """
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type."
        )

    user_id = payload.get("id")
    username = payload.get("sub")
    token_version = payload.get("token_version")
    jti = payload.get("jti")

    if user_id is None or username is None or token_version is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    redis_client = request.app.state.redis
    redis_key = f"refresh:{user_id}:{jti}"
    stored_token = redis_client.get(redis_key)

    if stored_token != body.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, username, is_deleted, token_version
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        if user["is_deleted"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deleted."
            )

        if user["token_version"] != token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        new_access_token = create_access_token(
            username=user["username"],
            user_id=user["id"],
            token_version=user["token_version"],
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        new_refresh_token = create_refresh_token(
            username=user["username"],
            user_id=user["id"],
            token_version=user["token_version"],
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        new_refresh_payload = decode_token(new_refresh_token)
        new_jti = new_refresh_payload["jti"]
        new_redis_key = f"refresh:{user['id']}:{new_jti}"
        session_set_key = f"user_refresh_tokens:{user['id']}"

        # 古い refresh token を削除
        redis_client.delete(redis_key)
        redis_client.srem(session_set_key, redis_key)

        # 新しい refresh token を保存
        redis_client.setex(
            new_redis_key,
            60 * 60 * 24 * REFRESH_TOKEN_EXPIRE_DAYS,
            new_refresh_token
        )
        redis_client.sadd(session_set_key, new_redis_key)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    finally:
        cursor.close()
        conn.close()


@router.post("/logout")
async def logout(
    request: Request,
    body: LogoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    ログアウトAPI

    処理の流れ:
    1. refresh token を検証
    2. Redis から対象の refresh token を削除
    """
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type."
        )

    user_id = payload.get("id")
    jti = payload.get("jti")

    if user_id is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed."
        )

    redis_client = request.app.state.redis
    redis_key = f"refresh:{user_id}:{jti}"
    session_set_key = f"user_refresh_tokens:{user_id}"

    redis_client.delete(redis_key)
    redis_client.srem(session_set_key, redis_key)

    return {
        "message": "Logged out successfully."
    }


@router.patch("/password")
async def change_password(
    request: Request,
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    パスワード変更API

    処理の流れ:
    1. 現在のログインユーザーを取得
    2. 現在のパスワードを確認
    3. 新しいパスワードをハッシュ化
    4. DB のパスワードを更新
    5. token_version を増加させる
    6. Redis の refresh token を全削除する
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, username, hashed_password, is_deleted, token_version
            FROM users
            WHERE id = %s
            """,
            (current_user["id"],)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        if user["is_deleted"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deleted."
            )

        if not verify_password(body.current_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )

        if verify_password(body.new_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password."
            )

        new_hashed_password = hash_password(body.new_password)

        cursor.execute(
            """
            UPDATE users
            SET hashed_password = %s,
                token_version = token_version + 1
            WHERE id = %s
            """,
            (new_hashed_password, user["id"])
        )
        conn.commit()

        redis_client = request.app.state.redis
        delete_all_user_refresh_tokens(redis_client, user["id"])

        return {
            "message": "Password changed successfully."
        }

    finally:
        cursor.close()
        conn.close()


@router.delete("/me")
async def delete_user(
    request: Request,
    body: DeleteUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    退会API

    処理の流れ:
    1. 現在のログインユーザーを取得
    2. 本人確認のためパスワードを確認
    3. soft delete を行う
    4. token_version を増加させる
    5. Redis の refresh token を全削除する
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, username, hashed_password, is_deleted, token_version
            FROM users
            WHERE id = %s
            """,
            (current_user["id"],)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        if user["is_deleted"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already deleted."
            )

        if not verify_password(body.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect."
            )

        cursor.execute(
            """
            UPDATE users
            SET is_deleted = TRUE,
                deleted_at = NOW(),
                token_version = token_version + 1
            WHERE id = %s
            """,
            (user["id"],)
        )
        conn.commit()

        redis_client = request.app.state.redis
        delete_all_user_refresh_tokens(redis_client, user["id"])

        return {
            "message": "User deleted successfully."
        }

    finally:
        cursor.close()
        conn.close()
