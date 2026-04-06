from pydantic import BaseModel, Field


# =========================
# 予測レスポンス
# =========================
class PredictionResponse(BaseModel):
    image_name: str
    prediction: str
    confidence: float


# =========================
# 認証関連スキーマ
# =========================
class CreateUserRequest(BaseModel):
    """
    ユーザー登録リクエスト
    """
    username: str = Field(..., min_length=4, max_length=30)
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """
    JWTトークンレスポンス
    """
    access_token: str
    token_type: str


class ChangePasswordRequest(BaseModel):
    """
    パスワード変更リクエスト

    - current_password: 現在のパスワード
    - new_password: 新しいパスワード
    """
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class DeleteUserRequest(BaseModel):
    """
    会員退会リクエスト

    - password: 本人確認のための現在のパスワード
    """
    password: str = Field(..., min_length=8, max_length=128)
