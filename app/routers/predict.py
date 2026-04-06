import os
import uuid
import hashlib
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from app.services.inference_service import run_inference
from app.db.database import get_connection
from app.schemas import PredictionResponse, UploadHistoryResponse
from app.auth.security import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    画像アップロードおよび推論API

    - ログイン済みユーザーのみ利用可能
    - アップロード情報と推論結果をDBに保存
    """

    # 1) Content-Type を検証
    if not file.content_type or file.content_type.lower() not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jpg, jpeg, png, webp 形式の画像ファイルのみアップロードできます。"
        )

    # 2) ファイルを読み込み
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="空のファイルはアップロードできません。"
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ファイルサイズは最大 {MAX_FILE_SIZE // (1024 * 1024)}MB までです。"
        )

    # 3) 実際に有効な画像かどうかを検証
    try:
        img = Image.open(BytesIO(file_bytes))
        img.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="有効な画像ファイルではありません。"
        )

    # 4) UUID ベースの保存ファイル名を生成
    original_filename = file.filename or "uploaded_image"
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()

    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        content_type_to_ext = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        ext = content_type_to_ext.get(file.content_type.lower(), ".jpg")

    user_id = current_user["id"]

    user_upload_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(user_upload_dir, stored_filename)

    # 5) ファイルを保存
    try:
        with open(stored_path, "wb") as f:
            f.write(file_bytes)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="アップロードファイルの保存中にエラーが発生しました。"
        )

    # 6) ファイルハッシュとサイズを計算
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    file_size = len(file_bytes)

    # 7) 推論を実行
    try:
        result = run_inference(file_bytes, original_filename)
    except Exception:
        if os.path.exists(stored_path):
            os.remove(stored_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像推論中にエラーが発生しました。"
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # アップロード画像情報を保存
        cursor.execute(
            """
            INSERT INTO uploaded_images (
                user_id,
                original_filename,
                stored_path,
                mime_type,
                file_size,
                file_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                original_filename,
                stored_path,
                file.content_type,
                file_size,
                file_hash,
            )
        )
        image_id = cursor.lastrowid

        # 推論結果を保存
        cursor.execute(
            """
            INSERT INTO predictions (
                image_id,
                user_id,
                label,
                confidence,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (image_id, user_id, result["prediction"], result["confidence"], "success")
        )

        conn.commit()

    except Exception:
        conn.rollback()
        if os.path.exists(stored_path):
            os.remove(stored_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="予測結果の保存中にエラーが発生しました。"
        )

    finally:
        cursor.close()
        conn.close()

    return result


@router.get("/uploads/history", response_model=UploadHistoryResponse)
async def get_upload_history(
    current_user: dict = Depends(get_current_user)
):
    """
    ユーザー別アップロード履歴 조회API
    - ログイン済みユーザーのみ利用可能
    - 自分がアップロードした画像と推論結果のみ返す
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                ui.id AS image_id,
                ui.original_filename,
                ui.stored_path,
                ui.mime_type,
                ui.file_size,
                ui.created_at AS uploaded_at,
                p.label AS prediction,
                p.confidence,
                p.status,
                p.created_at AS predicted_at
            FROM uploaded_images ui
            JOIN predictions p ON ui.id = p.image_id
            WHERE ui.user_id = %s
            ORDER BY ui.id DESC
            """,
            (current_user["id"],)
        )

        rows = cursor.fetchall()
        return {"items": rows}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="アップロード履歴の取得中にエラーが発生しました。"
        )

    finally:
        cursor.close()
        conn.close()
