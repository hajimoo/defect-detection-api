from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.db.database import get_connection
from app.auth.security import hash_password, verify_password, create_access_token
from app.schemas import CreateUserRequest, TokenResponse

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
        # 既に同じ username が存在するか確認する
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

        # パスワードは平文で保存せず、必ずハッシュ化して保存する
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

    注意:
    - このAPIは JSON ではなく、
      OAuth2PasswordRequestForm 形式で値を受け取る
    - Swagger UI の Authorize ボタンでもこのAPIが使われる

    処理の流れ:
    1. username でユーザー検索
    2. パスワード照合
    3. 成功したら JWT を発行
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # username でユーザー情報を取得する
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE username = %s",
            (form_data.username,)
        )
        user = cursor.fetchone()

        # ユーザーが存在しない場合
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
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
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    finally:
        cursor.close()
        conn.close()
