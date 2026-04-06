from pydantic import BaseModel, Field
from typing import List, Optional


class UploadHistoryItem(BaseModel):
    image_id: int
    original_filename: str
    stored_path: str
    mime_type: str
    file_size: int
    uploaded_at: Optional[str] = None
    prediction: str
    confidence: float
    status: str
    predicted_at: Optional[str] = None

class UploadHistoryResponse(BaseModel):
    items: List[UploadHistoryItem]


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
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    """
    リフレッシュトークンリクエスト
    """
    refresh_token: str


class LogoutRequest(BaseModel):
    """
    ログアウトリクエスト
    """
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """
    パスワード変更リクエスト
    """
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class DeleteUserRequest(BaseModel):
    """
    会員退会リクエスト
    """
    password: str = Field(..., min_length=8, max_length=128)
