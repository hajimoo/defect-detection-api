import os
import hashlib

from fastapi import APIRouter, UploadFile, File, Depends
from app.services.inference_service import run_inference
from app.db.database import get_connection
from app.schemas import PredictionResponse
from app.auth.security import get_current_user

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    画像アップロードおよび推論API

    このAPIはログイン済みユーザーのみ利用可能。
    JWT を検証し、現在のユーザー情報を取得してから
    アップロード情報と推論結果をDBに保存する。
    """
    file_bytes = await file.read()

    # アップロードされたファイルを保存する
    stored_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    # ファイルのハッシュ値とサイズを計算する
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    file_size = len(file_bytes)

    # 推論を実行する
    result = run_inference(file_bytes, file.filename)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 現在ログイン中のユーザーIDを取得する
        user_id = current_user["id"]

        # アップロード画像情報を保存する
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
            (user_id, file.filename, stored_path, file.content_type, file_size, file_hash)
        )
        image_id = cursor.lastrowid

        # 推論結果を保存する
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

    except Exception as e:
        conn.rollback()
        if os.path.exists(stored_path):
            os.remove(stored_path)
        raise e

    finally:
        cursor.close()
        conn.close()

    return result
