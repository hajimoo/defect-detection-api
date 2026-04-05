from pydantic import BaseModel

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
    username: str
    password: str


class TokenResponse(BaseModel):
    """
    JWTトークンレスポンス
    """
    access_token: str
    token_type: str
