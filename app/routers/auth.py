from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.db.database import get_connection
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.schemas import (
    CreateUserRequest,
    TokenResponse,
    ChangePasswordRequest,
    DeleteUserRequest,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
        # 同じ username が既に存在するか確認する
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

        # パスワードをハッシュ化して保存する
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
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    ログインAPI

    処理の流れ:
    1. username でユーザー検索
    2. 退会済みユーザーか確認
    3. パスワード照合
    4. 成功したら JWT を発行
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # username でユーザー情報を取得する
        cursor.execute(
            """
            SELECT id, username, hashed_password, is_deleted, token_version
            FROM users
            WHERE username = %s
            """,
            (form_data.username,)
        )
        user = cursor.fetchone()

        # ユーザーが存在しない場合
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        # 退会済みユーザーはログイン不可
        if user["is_deleted"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deleted."
            )

        # 入力されたパスワードとDB上のハッシュを照合する
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        # JWT に入れる情報を作成する
        access_token = create_access_token(
            username=user["username"],
            user_id=user["id"],
            token_version=user["token_version"],
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    finally:
        cursor.close()
        conn.close()


@router.patch("/password")
async def change_password(
    request: ChangePasswordRequest,
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
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 現在のユーザー情報を再取得する
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

        # 現在のパスワード確認
        if not verify_password(request.current_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )

        # 同じパスワードへの変更を防止する
        if verify_password(request.new_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password."
            )

        # 新しいパスワードをハッシュ化する
        new_hashed_password = hash_password(request.new_password)

        # パスワード更新 + token_version 増加
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

        return {
            "message": "Password changed successfully."
        }

    finally:
        cursor.close()
        conn.close()


@router.delete("/me")
async def delete_user(
    request: DeleteUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    退会API

    処理の流れ:
    1. 現在のログインユーザーを取得
    2. 本人確認のためパスワードを確認
    3. soft delete を行う
    4. token_version を増加させる
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 現在のユーザー情報を再取得する
        cursor.execute(
            """
            SELECT id, username, hashed_password, is_deleted
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

        # 本人確認のため現在のパスワードを確認する
        if not verify_password(request.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect."
            )

        # soft delete を行う
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

        return {
            "message": "User deleted successfully."
        }

    finally:
        cursor.close()
        conn.close()
